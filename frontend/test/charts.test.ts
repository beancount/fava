import { deepEqual, equal, ok } from "node:assert/strict";
import { test } from "node:test";

import { bar } from "../src/charts/bar.ts";
import {
  colors10,
  colors15,
  filterTicks,
  includeZero,
  padExtent,
} from "../src/charts/helpers.ts";
import { hierarchy, HierarchyChart } from "../src/charts/hierarchy.ts";
import { parseChartData } from "../src/charts/index.ts";
import { balances, LineChart } from "../src/charts/line.ts";
import { ScatterPlot, scatterplot } from "../src/charts/scatterplot.ts";
import { loadJSONSnapshot } from "./helpers.ts";

test("chart helpers (filter ticks)", () => {
  deepEqual(filterTicks(["1", "2", "3"], 2), ["1", "3"]);
  deepEqual(filterTicks(["1", "2", "3"], 4), ["1", "2", "3"]);
});

test("chart helpers (color scales)", () => {
  equal(colors10[0], "rgb(126, 174, 253)");
  equal(colors15[0], "rgb(173, 200, 254)");
});

test("chart helpers (include zero in extent)", () => {
  deepEqual(includeZero([2, 5]), [0, 5]);
  deepEqual(includeZero([-12, -5]), [-12, 0]);
  deepEqual(includeZero([-5, 5]), [-5, 5]);
  deepEqual(includeZero([undefined, undefined]), [0, 1]);
});

test("chart helpers (pad extent)", () => {
  deepEqual(padExtent([0, 1]), [-0.03, 1.03]);
  deepEqual(padExtent([undefined, undefined]), [0, 1]);
});

test("handle data for hierarchical chart", async () => {
  const ctx = { currencies: ["USD"], dateFormat: () => "DATE" };
  ok(hierarchy("name", "", ctx).is_err);
  const data = await loadJSONSnapshot("test_internal_api-test_chart_api.json");
  const parsed = parseChartData(data, ctx).unwrap()[0];
  ok(parsed instanceof HierarchyChart);
  deepEqual(parsed.currencies, ["USD"]);
  ok(parsed.data.get("USD"));
});

test("handle data for balances chart", () => {
  ok(balances("name", "").is_err);
  const data: unknown = [
    { date: "2000-01-01", balance: { EUR: 10, USD: 10 } },
    { date: "2000-02-01", balance: { EUR: 10 } },
  ];
  const parsed = balances("name", data).unwrap();
  ok(parsed instanceof LineChart);
  deepEqual(parsed.filter([]), [
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
  ok(scatterplot("name", "").is_err);
  const data: unknown = [
    { type: "test", date: "2000-01-01", description: "desc" },
  ];
  const parsed = scatterplot("name", data).unwrap();
  deepEqual(
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
  equal(true, chart.hasStackedData);
  deepEqual(chart.accounts, [
    "Expenses:Dining",
    "Expenses:Shoes",
    "Expenses:Taxes",
    "Expenses:Transportation",
  ]);
  const result = chart.filter([]);
  const simplified_stacks = result.stacks.map(([currency, series_arr]) => [
    currency,
    series_arr.map((series) => ({
      key: series.key,
      index: series.index,
      points: series.map((p) => [p[0], p[1]]),
    })),
  ]);
  deepEqual(simplified_stacks, [
    [
      "EUR",
      [
        {
          key: "Expenses:Dining",
          index: 0,
          points: [
            [0, 0],
            [0, 0],
          ],
        },
        {
          key: "Expenses:Shoes",
          index: 1,
          points: [
            [0, 0],
            [0, 60],
          ],
        },
        {
          key: "Expenses:Taxes",
          index: 2,
          points: [
            [0, 4],
            [60, 100],
          ],
        },
        {
          key: "Expenses:Transportation",
          index: 3,
          points: [
            [4, 10],
            [0, 0],
          ],
        },
      ],
    ],
    [
      "USD",
      [
        {
          key: "Expenses:Dining",
          index: 0,
          points: [
            [0, 8],
            [0, 0],
          ],
        },
        {
          key: "Expenses:Shoes",
          index: 1,
          points: [
            [0, 0],
            [0, 0],
          ],
        },
        {
          key: "Expenses:Taxes",
          index: 2,
          points: [
            [8, 10],
            [0, 0],
          ],
        },
        {
          key: "Expenses:Transportation",
          index: 3,
          points: [
            [0, 0],
            [0, 0],
          ],
        },
      ],
    ],
  ]);
  deepEqual(result.bar_groups, [
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
  equal(false, chart.hasStackedData);
  deepEqual(chart.filter([]).stacks, [
    ["EUR", []],
    ["USD", []],
  ]);
  const without_usd = chart.filter(["USD"]);
  deepEqual(without_usd.stacks, [["EUR", []]]);
  deepEqual(without_usd.bar_groups, [
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
  equal(false, chart.hasStackedData);
  deepEqual(chart.filter([]).stacks, [
    ["USD", []],
    ["AUD", []],
  ]);
  deepEqual(chart.filter([]).bar_groups, [
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
