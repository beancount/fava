import { test } from "uvu";
import assert from "uvu/assert";

import { bar } from "../src/charts/bar";
import { balances, commodities } from "../src/charts/line";
import {
  parseGroupedQueryChart,
  parseQueryChart,
} from "../src/charts/query-charts";
import { scatterplot } from "../src/charts/scatterplot";
import type { Result } from "../src/lib/result";

function force_ok<T>(r: Result<T, unknown>): T {
  if (!r.success) {
    throw new Error("Expected successful result");
  }
  return r.value;
}

const ctx = { currencies: ["EUR"], dateFormat: () => "DATE" };

test("handle data for balances chart", () => {
  assert.is(false, balances("").success);
  const data: unknown = [
    { date: "2000-01-01", balance: { EUR: 10, USD: 10 } },
    { date: "2000-02-01", balance: { EUR: 10 } },
  ];
  const parsed = force_ok(balances(data));

  assert.equal(parsed.data, [
    {
      name: "EUR",
      values: [
        { date: new Date("2000-01-01"), name: "EUR", value: 10 },
        { date: new Date("2000-02-01"), name: "EUR", value: 10 },
      ],
    },
    {
      name: "USD",
      values: [{ date: new Date("2000-01-01"), name: "USD", value: 10 }],
    },
  ]);
  const queryChart = parseQueryChart(data, ctx);
  assert.equal(queryChart.success && queryChart.value.data, parsed.data);
});

test("handle data for commodities chart", () => {
  assert.is(false, commodities("", null, "asdf").success);
  const data: unknown = {
    base: "EUR",
    quote: "USD",
    prices: [
      ["2000-01-01", 10.0],
      ["2000-02-01", 12.0],
    ],
  };
  const parsed = force_ok(commodities(data, null, "asdf"));
  assert.equal(parsed.data, [
    {
      name: "asdf",
      values: [
        { date: new Date("2000-01-01"), name: "asdf", value: 10 },
        { date: new Date("2000-02-01"), name: "asdf", value: 12 },
      ],
    },
  ]);
});

test("handle data for scatterplot chart", () => {
  assert.is(false, scatterplot("").success);
  const data: unknown = [
    { type: "test", date: "2000-01-01", description: "desc" },
  ];
  const parsed = force_ok(scatterplot(data));
  assert.is(parsed.data.length, 1);
  assert.equal(parsed, {
    data: [{ date: new Date("2000-01-01"), description: "desc", type: "test" }],
    type: "scatterplot",
  });
});

test("handle data for query charts", () => {
  const d = [{ group: "Assets:Cash", balance: { EUR: 10 } }];
  const { data } = force_ok(parseGroupedQueryChart(d, ctx));
  assert.is(data.get("EUR")?.value, 10);
  assert.equal(
    data
      .get("EUR")
      ?.descendants()
      .map((n) => n.data.account),
    ["(root)", "Assets", "Assets:Cash"]
  );
});

test("handle invalid data for query charts", () => {
  const d: unknown[] = [{}];
  const c = parseQueryChart(d, ctx);
  assert.is(false, c.success);
});

test("handle data for bar chart with stacked data", () => {
  const data: unknown = [
    {
      date: "2000-01-01",
      balance: { EUR: 10, USD: 10 },
      budgets: { USD: 20 },
      account_balances: {
        "Expenses:Dining": { USD: 8 },
        "Expenses:Transportation": { EUR: 6 },
        "Expenses:Taxes": { USD: 2, EUR: 4 },
      },
    },
    {
      date: "2000-02-01",
      balance: { EUR: 100 },
      budgets: { EUR: 50 },
      account_balances: {
        "Expenses:Shoes": { EUR: 60 },
        "Expenses:Taxes": { EUR: 40 },
      },
    },
  ];
  const ctx2 = { currencies: ["EUR", "USD"], dateFormat: () => "DATE" };
  const parsed = force_ok(bar(data, ctx2));
  const parsed_data = parsed.data.map((d) => ({
    ...d,
    values: d.values.map((v) => ({
      ...v,
      children: Object.fromEntries(v.children),
    })),
  }));
  assert.is(true, parsed.hasStackedData);
  assert.equal(parsed_data, [
    {
      date: new Date("2000-01-01"),
      label: "DATE",
      values: [
        {
          name: "EUR",
          value: 10,
          children: {
            "Expenses:Dining": 0,
            "Expenses:Transportation": 6,
            "Expenses:Taxes": 4,
          },
          budget: 0,
        },
        {
          name: "USD",
          value: 10,
          children: {
            "Expenses:Dining": 8,
            "Expenses:Transportation": 0,
            "Expenses:Taxes": 2,
          },
          budget: 20,
        },
      ],
    },
    {
      date: new Date("2000-02-01"),
      label: "DATE",
      values: [
        {
          name: "EUR",
          value: 100,
          children: {
            "Expenses:Shoes": 60,
            "Expenses:Taxes": 40,
          },
          budget: 50,
        },
        {
          name: "USD",
          value: 0,
          children: {
            "Expenses:Shoes": 0,
            "Expenses:Taxes": 0,
          },
          budget: 0,
        },
      ],
    },
  ]);
});
test("handle data for bar chart without stacked data", () => {
  const data: unknown = [
    {
      date: "2000-01-01",
      balance: { EUR: 10, USD: 10 },
      budgets: { USD: 20 },
      account_balances: {},
    },
    {
      date: "2000-02-01",
      balance: { EUR: 100 },
      budgets: { EUR: 50 },
      account_balances: {},
    },
  ];
  const ctx2 = { currencies: ["EUR", "USD"], dateFormat: () => "DATE" };
  const parsed = force_ok(bar(data, ctx2));
  const parsed_data = parsed.data.map((d) => ({
    ...d,
    values: d.values.map((v) => ({
      ...v,
      children: Object.fromEntries(v.children),
    })),
  }));
  assert.is(false, parsed.hasStackedData);
  assert.equal(parsed_data, [
    {
      date: new Date("2000-01-01"),
      label: "DATE",
      values: [
        { name: "EUR", value: 10, children: {}, budget: 0 },
        { name: "USD", value: 10, children: {}, budget: 20 },
      ],
    },
    {
      date: new Date("2000-02-01"),
      label: "DATE",
      values: [
        { name: "EUR", value: 100, children: {}, budget: 50 },
        { name: "USD", value: 0, children: {}, budget: 0 },
      ],
    },
  ]);
});
test.run();
