import test from "ava";

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

test("handle data for balances chart", (t) => {
  t.false(balances("").success);
  const data: unknown = [
    { date: "2000-01-01", balance: { EUR: 10, USD: 10 } },
    { date: "2000-02-01", balance: { EUR: 10 } },
  ];
  const parsed = force_ok(balances(data));
  // two currencies
  t.is(parsed.data.length, 2);
  t.is(parsed.data[0].values.length, 2);
  t.is(parsed.data[1].values.length, 1);
  const queryChart = parseQueryChart(data, ctx);
  t.deepEqual(queryChart.success && queryChart.value.data, parsed.data);
  t.snapshot(parsed);
});

test("handle data for commodities chart", (t) => {
  t.false(commodities("", null, "asdf").success);
  const data: unknown = {
    base: "EUR",
    quote: "USD",
    prices: [
      ["2000-01-01", 10.0],
      ["2000-02-01", 12.0],
    ],
  };
  const parsed = force_ok(commodities(data, null, "asdf"));
  t.is(parsed.data.length, 1);
  t.is(parsed.data[0].values.length, 2);
  t.snapshot(parsed);
});

test("handle data for scatterplot chart", (t) => {
  t.false(scatterplot("").success);
  const data: unknown = [
    { type: "test", date: "2000-01-01", description: "desc" },
  ];
  const parsed = force_ok(scatterplot(data));
  t.is(parsed.data.length, 1);
  t.snapshot(parsed);
});

test("handle data for query charts", (t) => {
  const d = [{ group: "Assets:Cash", balance: { EUR: 10 } }];
  const { data } = force_ok(parseGroupedQueryChart(d, ctx));
  t.is(data.get("EUR")?.value, 10);
  t.deepEqual(
    data
      .get("EUR")
      ?.descendants()
      .map((n) => n.data.account),
    ["(root)", "Assets", "Assets:Cash"]
  );
});

test("handle invalid data for query charts", (t) => {
  const d: unknown[] = [{}];
  const c = parseQueryChart(d, ctx);
  t.false(c.success);
});
