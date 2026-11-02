import { equal } from "node:assert/strict";
import { test } from "node:test";

import {
  day,
  formatter_context,
  get_date_format,
  locale_formatter,
  month,
  quarter,
  week,
  year,
} from "../src/format.ts";
import { FiscalYearEnd } from "../src/lib/interval.ts";

const UK_FYE = new FiscalYearEnd(4, 5);
const AU_NZ_FYE = new FiscalYearEnd(6, 30);

test("locale number formatting", () => {
  const f = locale_formatter(null);
  const de = locale_formatter("de_DE");
  const ind = locale_formatter("en_IN");
  equal(f(10), "10.00");
  equal(de(10), "10,00");
  equal(ind(10), "10.00");
  equal(f(1000000), "1000000.00");
  equal(de(1000000.000002), "1.000.000,00");
  equal(ind(1000000.00000001), "10,00,000.00");

  const es_ar = locale_formatter("es_AR", 2);
  equal(es_ar(1234.1234), "1.234,12");

  // it silently clamps large or negative precisions
  const de_large = locale_formatter("de_DE", 100);
  equal(de_large(1000), "1.000,00000000000000000000");
  const de_negative = locale_formatter("de_DE", -100);
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

test("date formatting: days", () => {
  equal(day(new Date("0999-01-01")), "0999-01-01");
  equal(day(new Date("2020-01-01")), "2020-01-01");
  equal(day(new Date("2020-03-20")), "2020-03-20");
});

test("date formatting: weeks", () => {
  equal(week(new Date("2021-01-01")), "2020-W53");
  equal(week(new Date("2020-01-01")), "2020-W01");
  equal(week(new Date("2020-03-20")), "2020-W12");
});

test("date formatting: months", () => {
  equal(month(new Date("2020-01-01")), "2020-01");
  equal(month(new Date("2020-03-20")), "2020-03");
});

test("date formatting: quarter", () => {
  equal(quarter(new Date("0999-02-01")), "999-Q1");
  equal(quarter(new Date("2020-01-01")), "2020-Q1");
  equal(quarter(new Date("2020-03-20")), "2020-Q1");
});

test("date formatting: year", () => {
  equal(year(new Date("0999-02-01")), "0999");
  equal(year(new Date("2020-01-01")), "2020");
  equal(year(new Date("2020-03-20")), "2020");
});

test("date formatting: fiscal year", () => {
  const fiscal_year = get_date_format("fiscal_year", FiscalYearEnd.default);
  equal(fiscal_year(new Date("2020-01-01")), "FY2020");
  const uk_fiscal_year = get_date_format("fiscal_year", UK_FYE);
  equal(uk_fiscal_year(new Date("2020-04-05")), "FY2020");
  equal(uk_fiscal_year(new Date("2020-04-06")), "FY2021");
});

test("date formatting: fiscal quarter", () => {
  const fiscal_quarter = get_date_format(
    "fiscal_quarter",
    FiscalYearEnd.default,
  );
  equal(fiscal_quarter(new Date("2020-03-20")), "FY2020-Q1");

  const uk_fiscal_quarter = get_date_format("fiscal_quarter", UK_FYE);
  equal(uk_fiscal_quarter(new Date("2020-01-01")), "FY2020-Q4");

  const au_nz_fiscal_quarter = get_date_format("fiscal_quarter", AU_NZ_FYE);
  equal(au_nz_fiscal_quarter(new Date("2020-03-20")), "FY2020-Q3");
});
