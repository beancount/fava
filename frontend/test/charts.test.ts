import test from "ava";

import {
  balances,
  commodities,
  parseGroupedQueryChart,
  parseQueryChart,
  scatterplot,
} from "../src/charts";

test("handle data for balances chart", (t) => {
  t.throws(() => balances(""));
  const data: unknown = [
    { date: "2000-01-01", balance: { EUR: 10, USD: 10 } },
    { date: "2000-02-01", balance: { EUR: 10 } },
  ];
  const parsed = balances(data);
  // two currencies
  t.is(parsed.data.length, 2);
  t.is(parsed.data[0].values.length, 2);
  t.is(parsed.data[1].values.length, 1);
  const queryChart = parseQueryChart(data);
  t.deepEqual(queryChart?.data, parsed.data);
  t.snapshot(parsed);
});

test("handle data for commodities chart", (t) => {
  t.throws(() => commodities("", "asdf"));
  const data: unknown = {
    base: "EUR",
    quote: "USD",
    prices: [
      ["2000-01-01", 10.0],
      ["2000-02-01", 12.0],
    ],
  };
  const parsed = commodities(data, "asdf");
  t.is(parsed.data.length, 1);
  t.is(parsed.data[0].values.length, 2);
  t.snapshot(parsed);
});

test("handle data for scatterplot chart", (t) => {
  t.throws(() => scatterplot(""));
  const data: unknown = [
    { type: "test", date: "2000-01-01", description: "desc" },
  ];
  const parsed = scatterplot(data);
  t.is(parsed.data.length, 1);
  t.snapshot(parsed);
});

test("handle data for query charts", (t) => {
  const d = [{ group: "Assets:Cash", balance: { EUR: 10 } }];
  const c = parseGroupedQueryChart(d, ["EUR"]);
  t.is(c?.data.get("EUR")?.value, 10);
  t.deepEqual(
    c?.data
      .get("EUR")
      ?.descendants()
      .map((n) => n.data.account),
    ["(root)", "Assets", "Assets:Cash"]
  );
});

test("handle invalid data for query charts", (t) => {
  const d: unknown[] = [{}];
  const c = parseQueryChart(d);
  t.is(c, null);
});
