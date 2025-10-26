import { deepEqual, equal } from "node:assert/strict";
import { test } from "node:test";

import {
  dateFormat,
  formatter_context,
  localeFormatter,
  timeFilterDateFormat,
} from "../src/format.ts";

test("locale number formatting", () => {
  const f = localeFormatter(null);
  const de = localeFormatter("de_DE");
  const ind = localeFormatter("en_IN");
  equal(f(10), "10.00");
  equal(de(10), "10,00");
  equal(ind(10), "10.00");
  equal(f(1000000), "1000000.00");
  equal(de(1000000.000002), "1.000.000,00");
  equal(ind(1000000.00000001), "10,00,000.00");

  const es_ar = localeFormatter("es_AR", 2);
  equal(es_ar(1234.1234), "1.234,12");

  // it silently clamps large or negative precisions
  const de_large = localeFormatter("de_DE", 100);
  equal(de_large(1000), "1.000,00000000000000000000");
  const de_negative = localeFormatter("de_DE", -100);
  equal(de_negative(1000), "1.000");
});

test("formatter context", () => {
  const ctx = formatter_context(false, null, {});
  equal(ctx.num(10, "EUR"), "10.00");
  equal(ctx.amount(10, "EUR"), "10.00 EUR");

  const de_ctx = formatter_context(false, "de_DE", { EUR: 1 });
  equal(de_ctx.num(10, "EUR"), "10,0");
  equal(de_ctx.amount(10, "EUR"), "10,0 EUR");
  equal(de_ctx.amount(10, "USD"), "10,00 USD");

  const incognito_ctx = formatter_context(true, null, { USD: 4 });
  equal(incognito_ctx.num(10, "EUR"), "XX.XX");
  equal(incognito_ctx.num(10, "USD"), "XX.XXXX");
});

test("time filter date formatting", () => {
  const { day, month, week, quarter, year, ...rest } = timeFilterDateFormat;
  deepEqual(rest, {});
  const janfirst = new Date("2020-01-01");
  const date = new Date("2020-03-20");
  equal(day(janfirst), "2020-01-01");
  equal(day(date), "2020-03-20");
  equal(month(janfirst), "2020-01");
  equal(month(date), "2020-03");
  equal(week(janfirst), "2020-W01");
  equal(week(date), "2020-W12");
  equal(quarter(janfirst), "2020-Q1");
  equal(quarter(date), "2020-Q1");
  equal(year(janfirst), "2020");
  equal(year(date), "2020");
});

test("human-readable date formatting", () => {
  const { day, month, week, quarter, year, ...rest } = dateFormat;
  deepEqual(rest, {});
  const janfirst = new Date("2020-01-01");
  const date = new Date("2020-03-20");
  equal(day(janfirst), "2020-01-01");
  equal(day(date), "2020-03-20");
  equal(month(janfirst), "Jan 2020");
  equal(month(date), "Mar 2020");
  equal(week(janfirst), "2020W01");
  equal(week(date), "2020W12");
  equal(quarter(janfirst), "2020Q1");
  equal(quarter(date), "2020Q1");
  equal(year(janfirst), "2020");
  equal(year(date), "2020");
});
