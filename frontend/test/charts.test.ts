import test from "ava";

import { balances } from "../src/charts";

test("barchart", (t) => {
  t.throws(() => balances(""));
  const data: unknown = [
    { date: "2000-01-01", balance: { EUR: 10, USD: 10 } },
    { date: "2000-02-01", balance: { EUR: 10 } },
  ];
  const parsed = balances(data);
  // two currencies
  t.deepEqual(parsed.data.length, 2);
  t.deepEqual(parsed.data[0].values.length, 2);
  t.deepEqual(parsed.data[1].values.length, 1);
  t.snapshot(parsed);
});
