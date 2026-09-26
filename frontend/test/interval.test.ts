import { deepEqual, equal, ok } from "node:assert/strict";
import { test } from "node:test";

import {
  FiscalYearEnd,
  get_interval,
  interval_label,
} from "../src/lib/interval.ts";

const default_fye = FiscalYearEnd.default;
const au_nz_fye = new FiscalYearEnd(6, 30);
const jp_fye = new FiscalYearEnd(15, 31);
const uk_fye = new FiscalYearEnd(4, 5);
const za_fye = new FiscalYearEnd(2, 28);

test("validate interval", () => {
  equal(get_interval("year", default_fye), "year");
  equal(get_interval("fiscal_year", default_fye), "month");
  equal(get_interval("fiscal_quarter", default_fye), "month");
  equal(get_interval("yasdfaear", default_fye), "month");
  equal(get_interval(null, default_fye), "month");

  equal(get_interval("year", uk_fye), "year");
  equal(get_interval("fiscal_year", uk_fye), "fiscal_year");
  equal(get_interval("fiscal_quarter", uk_fye), "month");
  equal(get_interval("fiscal_quarter", au_nz_fye), "fiscal_quarter");
});

test("interval labels", () => {
  equal(interval_label("fiscal_year"), "Per Fiscal Year");
  equal(interval_label("fiscal_quarter"), "Per Fiscal Quarter");
});

test("FiscalYearEnd fields", () => {
  equal(default_fye.month, 12);
  equal(default_fye.day, 31);

  equal(za_fye.month, 2);
  equal(za_fye.day, 28);

  equal(jp_fye.month, 15);
  equal(jp_fye.day, 31);
});

test("fiscal year available intervals", () => {
  deepEqual(default_fye.available_intervals, [
    "year",
    "quarter",
    "month",
    "week",
    "day",
  ]);
  deepEqual(au_nz_fye.available_intervals, [
    "year",
    "fiscal_year",
    "quarter",
    "fiscal_quarter",
    "month",
    "week",
    "day",
  ]);
  deepEqual(uk_fye.available_intervals, [
    "year",
    "fiscal_year",
    "quarter",
    "month",
    "week",
    "day",
  ]);
});

test("FiscalYearEnd.format_fiscal_year", () => {
  equal(uk_fye.format_year(new Date("2024-04-05")), "FY2024");
  equal(uk_fye.format_year(new Date("2024-04-06")), "FY2025");

  equal(za_fye.format_year(new Date("2023-02-28")), "FY2023");
  equal(za_fye.format_year(new Date("2023-03-01")), "FY2024");

  equal(jp_fye.format_year(new Date("2024-02-02")), "FY2023");
  equal(jp_fye.format_year(new Date("2024-03-31")), "FY2023");
  equal(jp_fye.format_year(new Date("2024-04-01")), "FY2024");
});

test("FiscalYearEnd.fiscal_quarter", () => {
  equal(au_nz_fye.format_quarter(new Date("2016-04-06")), "FY2016-Q4");
  equal(au_nz_fye.format_quarter(new Date("2016-01-01")), "FY2016-Q3");
  equal(au_nz_fye.format_quarter(new Date("2015-10-02")), "FY2016-Q2");

  equal(jp_fye.format_quarter(new Date("2015-11-01")), "FY2015-Q3");
  equal(jp_fye.format_quarter(new Date("2016-02-01")), "FY2015-Q4");
});

test("FiscalYearEnd.equals", () => {
  ok(au_nz_fye.equals(new FiscalYearEnd(6, 30)));
  ok(!au_nz_fye.equals(uk_fye));
  ok(!au_nz_fye.equals(new FiscalYearEnd(6, 29)));
});

test("FiscalYearEnd.validator", () => {
  const parsed = FiscalYearEnd.validator({ month: 6, day: 30 }).unwrap();
  ok(parsed instanceof FiscalYearEnd);
  equal(parsed.month, 6);
  equal(parsed.day, 30);

  ok(!FiscalYearEnd.validator({ month: 6 }).is_ok);
  ok(!FiscalYearEnd.validator({ month: "6", day: 30 }).is_ok);
  ok(!FiscalYearEnd.validator(null).is_ok);
});
