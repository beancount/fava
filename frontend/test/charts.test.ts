import { test } from "uvu";
import assert from "uvu/assert";

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

test.run();
