import { test } from "uvu";
import assert from "uvu/assert";

import { parseChartData } from "../src/charts";
import { bar } from "../src/charts/bar";
import { hierarchy, HierarchyChart } from "../src/charts/hierarchy";
import { balances, LineChart } from "../src/charts/line";
import {
  parseGroupedQueryChart,
  parseQueryChart,
} from "../src/charts/query-charts";
import { ScatterPlot, scatterplot } from "../src/charts/scatterplot";
import { parseJSON } from "../src/lib/json";

import { loadSnapshot } from "./end-to-end-validation.test";

test("handle data for hierarchical chart", async () => {
  const ctx = { currencies: ["USD"], dateFormat: () => "DATE" };
  assert.ok(hierarchy("name", "", ctx).is_err);
  const data = parseJSON(
    await loadSnapshot("test_internal_api.py-test_chart_api"),
  ).unwrap();
  const parsed = parseChartData(data, ctx).unwrap()[0];
  assert.ok(parsed instanceof HierarchyChart);
  assert.equal([...parsed.data.keys()], ["USD"]);
  assert.ok(parsed.data.get("USD"));
});

test("handle data for balances chart", () => {
  const ctx = { currencies: ["EUR"], dateFormat: () => "DATE" };
  assert.ok(balances("name", "").is_err);
  const data: unknown = [
    { date: "2000-01-01", balance: { EUR: 10, USD: 10 } },
    { date: "2000-02-01", balance: { EUR: 10 } },
  ];
  const parsed = balances("name", data).unwrap();
  assert.ok(parsed instanceof LineChart);
  assert.equal(parsed.filter([]), [
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
  const queryChart = parseQueryChart(data, ctx).unwrap();
  assert.ok(queryChart instanceof LineChart);
  assert.equal(queryChart.filter([]), parsed.filter([]));
});

test("handle data for scatterplot chart", () => {
  assert.ok(scatterplot("name", "").is_err);
  const data: unknown = [
    { type: "test", date: "2000-01-01", description: "desc" },
  ];
  const parsed = scatterplot("name", data).unwrap();
  assert.equal(
    parsed,
    new ScatterPlot("name", [
      { date: new Date("2000-01-01"), description: "desc", type: "test" },
    ]),
  );
});

test("handle data for query charts", () => {
  const ctx = { currencies: ["EUR"], dateFormat: () => "DATE" };
  const d = [{ group: "Assets:Cash", balance: { EUR: 10 } }];
  const { data } = parseGroupedQueryChart(d, ctx).unwrap();
  assert.is(data.get("EUR")?.value, 10);
  assert.equal(
    data
      .get("EUR")
      ?.descendants()
      .map((n) => n.data.account),
    ["(root)", "Assets", "Assets:Cash"],
  );
});

test("handle invalid data for query charts", () => {
  const ctx = { currencies: ["EUR"], dateFormat: () => "DATE" };
  const d: unknown[] = [{}];
  const c = parseQueryChart(d, ctx);
  assert.ok(c.is_err);
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
  const ctx = { currencies: ["EUR", "USD"], dateFormat: () => "DATE" };
  const chart = bar("name", data, ctx).unwrap();
  assert.is(true, chart.hasStackedData);
  assert.equal(chart.accounts, [
    "Expenses:Dining",
    "Expenses:Shoes",
    "Expenses:Taxes",
    "Expenses:Transportation",
  ]);
  assert.equal(chart.filter([]).stacks, [
    [
      "EUR",
      [
        [
          [0, 0],
          [0, 0],
        ],
        [
          [0, 0],
          [0, 60],
        ],
        [
          [0, 4],
          [60, 100],
        ],
        [
          [4, 10],
          [0, 0],
        ],
      ],
    ],
    [
      "USD",
      [
        [
          [0, 8],
          [0, 0],
        ],
        [
          [0, 0],
          [0, 0],
        ],
        [
          [8, 10],
          [0, 0],
        ],
        [
          [0, 0],
          [0, 0],
        ],
      ],
    ],
  ]);
  assert.equal(chart.filter([]).bar_groups, [
    {
      date: new Date("2000-01-01"),
      label: "DATE",
      values: [
        {
          currency: "EUR",
          value: 10,
          budget: 0,
        },
        {
          currency: "USD",
          value: 10,
          budget: 20,
        },
      ],
      account_balances: {
        "Expenses:Dining": { USD: 8 },
        "Expenses:Transportation": { EUR: 6 },
        "Expenses:Taxes": { USD: 2, EUR: 4 },
      },
    },
    {
      date: new Date("2000-02-01"),
      label: "DATE",
      values: [
        {
          currency: "EUR",
          value: 100,
          budget: 50,
        },
        {
          currency: "USD",
          value: 0,
          budget: 0,
        },
      ],
      account_balances: {
        "Expenses:Shoes": { EUR: 60 },
        "Expenses:Taxes": { EUR: 40 },
      },
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
  // even without the operating currencies, the two most popular ones will be selected
  const ctx = { currencies: [], dateFormat: () => "DATE" };
  const chart = bar("name", data, ctx).unwrap();
  assert.is(false, chart.hasStackedData);
  assert.equal(chart.filter([]).stacks, [
    ["EUR", []],
    ["USD", []],
  ]);
  const without_usd = chart.filter(["USD"]);
  assert.equal(without_usd.stacks, [["EUR", []]]);
  assert.equal(without_usd.bar_groups, [
    {
      date: new Date("2000-01-01"),
      label: "DATE",
      values: [{ currency: "EUR", value: 10, budget: 0 }],
      account_balances: {},
    },
    {
      date: new Date("2000-02-01"),
      label: "DATE",
      values: [{ currency: "EUR", value: 100, budget: 50 }],
      account_balances: {},
    },
  ]);
});

test("only use currencies in records for bar chart", () => {
  const data: unknown = [
    {
      date: "2000-01-01",
      balance: { AUD: 10, USD: 10 },
      budgets: { USD: 20 },
      account_balances: {},
    },
    {
      date: "2000-02-01",
      balance: { AUD: 100 },
      budgets: { AUD: 50 },
      account_balances: {},
    },
  ];
  const ctx = { currencies: ["EUR", "USD"], dateFormat: () => "DATE" };
  const chart = bar("name", data, ctx).unwrap();
  assert.is(false, chart.hasStackedData);
  assert.equal(chart.filter([]).stacks, [
    ["USD", []],
    ["AUD", []],
  ]);
  assert.equal(chart.filter([]).bar_groups, [
    {
      date: new Date("2000-01-01"),
      label: "DATE",
      values: [
        { currency: "USD", value: 10, budget: 20 },
        { currency: "AUD", value: 10, budget: 0 },
      ],
      account_balances: {},
    },
    {
      date: new Date("2000-02-01"),
      label: "DATE",
      values: [
        { currency: "USD", value: 0, budget: 0 },
        { currency: "AUD", value: 100, budget: 50 },
      ],
      account_balances: {},
    },
  ]);
});

test.run();
