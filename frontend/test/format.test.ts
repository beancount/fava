import test from "ava";

import {
  dateFormat,
  localeFormatter,
  timeFilterDateFormat,
} from "../src/format";

test("locale number formatting", (t) => {
  const f = localeFormatter(null);
  const de = localeFormatter("de_DE");
  const ind = localeFormatter("en_IN");
  t.is(f(10), "10.00");
  t.is(de(10), "10,00");
  t.is(ind(10), "10.00");
  t.is(f(1000000), "1000000.00");
  t.is(de(1000000), "1.000.000,00");
  t.is(ind(1000000), "10,00,000.00");
});

test("time filter date formatting", (t) => {
  const { day, month, week, quarter, year, ...rest } = timeFilterDateFormat;
  t.deepEqual(rest, {});
  const janfirst = new Date("2020-01-01");
  const date = new Date("2020-03-20");
  t.is(day(janfirst), "2020-01-01");
  t.is(day(date), "2020-03-20");
  t.is(month(janfirst), "2020-01");
  t.is(month(date), "2020-03");
  t.is(week(janfirst), "2020-W00");
  t.is(week(date), "2020-W11");
  t.is(quarter(janfirst), "2020-Q1");
  t.is(quarter(date), "2020-Q1");
  t.is(year(janfirst), "2020");
  t.is(year(date), "2020");
});

test("human-readable date formatting", (t) => {
  const { day, month, week, quarter, year, ...rest } = dateFormat;
  t.deepEqual(rest, {});
  const janfirst = new Date("2020-01-01");
  const date = new Date("2020-03-20");
  t.is(day(janfirst), "2020-01-01");
  t.is(day(date), "2020-03-20");
  t.is(month(janfirst), "Jan 2020");
  t.is(month(date), "Mar 2020");
  t.is(week(janfirst), "2020W00");
  t.is(week(date), "2020W11");
  t.is(quarter(janfirst), "2020Q1");
  t.is(quarter(date), "2020Q1");
  t.is(year(janfirst), "2020");
  t.is(year(date), "2020");
});
