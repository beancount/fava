import { test } from "uvu";
import * as assert from "uvu/assert";

import {
  dateFormat,
  formatter_context,
  localeFormatter,
  timeFilterDateFormat,
} from "../src/format";

test("locale number formatting", () => {
  const f = localeFormatter(null);
  const de = localeFormatter("de_DE");
  const ind = localeFormatter("en_IN");
  assert.is(f(10), "10.00");
  assert.is(de(10), "10,00");
  assert.is(ind(10), "10.00");
  assert.is(f(1000000), "1000000.00");
  assert.is(de(1000000.000002), "1.000.000,00");
  assert.is(ind(1000000.00000001), "10,00,000.00");

  const es_ar = localeFormatter("es_AR", 2);
  assert.is(es_ar(1234.1234), "1.234,12");

  // it silently clamps large or negative precisions
  const de_large = localeFormatter("de_DE", 100);
  assert.is(de_large(1000), "1.000,00000000000000000000");
  const de_negative = localeFormatter("de_DE", -100);
  assert.is(de_negative(1000), "1.000");
});

test("formatter context", () => {
  const ctx = formatter_context(false, null, {});
  assert.equal(ctx.num(10, "EUR"), "10.00");
  assert.equal(ctx.amount(10, "EUR"), "10.00 EUR");

  const de_ctx = formatter_context(false, "de_DE", { EUR: 1 });
  assert.equal(de_ctx.num(10, "EUR"), "10,0");
  assert.equal(de_ctx.amount(10, "EUR"), "10,0 EUR");
  assert.equal(de_ctx.amount(10, "USD"), "10,00 USD");

  const incognito_ctx = formatter_context(true, null, { USD: 4 });
  assert.equal(incognito_ctx.num(10, "EUR"), "XX.XX");
  assert.equal(incognito_ctx.num(10, "USD"), "XX.XXXX");
});

test("time filter date formatting", () => {
  const { day, month, week, quarter, year, ...rest } = timeFilterDateFormat;
  assert.equal(rest, {});
  const janfirst = new Date("2020-01-01");
  const date = new Date("2020-03-20");
  assert.is(day(janfirst), "2020-01-01");
  assert.is(day(date), "2020-03-20");
  assert.is(month(janfirst), "2020-01");
  assert.is(month(date), "2020-03");
  assert.is(week(janfirst), "2020-W01");
  assert.is(week(date), "2020-W12");
  assert.is(quarter(janfirst), "2020-Q1");
  assert.is(quarter(date), "2020-Q1");
  assert.is(year(janfirst), "2020");
  assert.is(year(date), "2020");
});

test("human-readable date formatting", () => {
  const { day, month, week, quarter, year, ...rest } = dateFormat;
  assert.equal(rest, {});
  const janfirst = new Date("2020-01-01");
  const date = new Date("2020-03-20");
  assert.is(day(janfirst), "2020-01-01");
  assert.is(day(date), "2020-03-20");
  assert.is(month(janfirst), "Jan 2020");
  assert.is(month(date), "Mar 2020");
  assert.is(week(janfirst), "2020W01");
  assert.is(week(date), "2020W12");
  assert.is(quarter(janfirst), "2020Q1");
  assert.is(quarter(date), "2020Q1");
  assert.is(year(janfirst), "2020");
  assert.is(year(date), "2020");
});

test.run();
