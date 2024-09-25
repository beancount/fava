import { test } from "uvu";
import assert from "uvu/assert";

import { parseChartData } from "../src/charts";
import { bar } from "../src/charts/bar";
import {
  colors10,
  colors15,
  filterTicks,
  includeZero,
  padExtent,
} from "../src/charts/helpers";
import { hierarchy, HierarchyChart } from "../src/charts/hierarchy";
import { balances, LineChart } from "../src/charts/line";
import { ScatterPlot, scatterplot } from "../src/charts/scatterplot";
import { loadJSONSnapshot } from "./helpers";

test("chart helpers (filter ticks)", () => {
  assert.equal(filterTicks(["1", "2", "3"], 2), ["1", "3"]);
  assert.equal(filterTicks(["1", "2", "3"], 4), ["1", "2", "3"]);
});

test("chart helpers (color scales)", () => {
  assert.equal(colors10[0], "rgb(126, 174, 253)");
  assert.equal(colors15[0], "rgb(173, 200, 254)");
});

test("chart helpers (include zero in extent)", () => {
  assert.equal(includeZero([2, 5]), [0, 5]);
  assert.equal(includeZero([-12, -5]), [-12, 0]);
  assert.equal(includeZero([-5, 5]), [-5, 5]);
  assert.equal(includeZero([undefined, undefined]), [0, 1]);
});

test("chart helpers (pad extent)", () => {
  assert.equal(padExtent([0, 1]), [-0.03, 1.03]);
  assert.equal(padExtent([undefined, undefined]), [0, 1]);
});

test("handle data for hierarchical chart", async () => {
  const ctx = { currencies: ["USD"], dateFormat: () => "DATE" };
  assert.ok(hierarchy("name", "", ctx).is_err);
  const data = await loadJSONSnapshot("test_internal_api-test_chart_api.json");
  const parsed = parseChartData(data, ctx).unwrap()[0];
  assert.ok(parsed instanceof HierarchyChart);
  assert.equal([...parsed.data.keys()], ["USD"]);
  assert.ok(parsed.data.get("USD"));
});

test("handle data for balances chart", () => {
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
