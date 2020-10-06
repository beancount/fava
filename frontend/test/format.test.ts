import test from "ava";
import {
  localeFormatter,
  timeFilterDateFormat,
  dateFormat,
} from "../src/format";

test("locale number formatting", (t) => {
  const f = localeFormatter(null);
  const de = localeFormatter("de_DE");
  const ind = localeFormatter("en_IN");
  t.deepEqual(f(10), "10.00");
  t.deepEqual(de(10), "10,00");
  t.deepEqual(ind(10), "10.00");
  t.deepEqual(f(1000000), "1000000.00");
  t.deepEqual(de(1000000), "1.000.000,00");
  t.deepEqual(ind(1000000), "10,00,000.00");
});

test("time filter date formatting", (t) => {
  const { day, month, week, quarter, year, ...rest } = timeFilterDateFormat;
  t.deepEqual(rest, {});
  const janfirst = new Date("2020-01-01");
  const date = new Date("2020-03-20");
  t.deepEqual(day(janfirst), "2020-01-01");
  t.deepEqual(day(date), "2020-03-20");
  t.deepEqual(month(janfirst), "2020-01");
  t.deepEqual(month(date), "2020-03");
  t.deepEqual(week(janfirst), "2020-W00");
  t.deepEqual(week(date), "2020-W11");
  t.deepEqual(quarter(janfirst), "2020-Q1");
  t.deepEqual(quarter(date), "2020-Q1");
  t.deepEqual(year(janfirst), "2020");
  t.deepEqual(year(date), "2020");
});

test("human-readable date formatting", (t) => {
  const { day, month, week, quarter, year, ...rest } = dateFormat;
  t.deepEqual(rest, {});
  const janfirst = new Date("2020-01-01");
  const date = new Date("2020-03-20");
  t.deepEqual(day(janfirst), "2020-01-01");
  t.deepEqual(day(date), "2020-03-20");
  t.deepEqual(month(janfirst), "Jan 2020");
  t.deepEqual(month(date), "Mar 2020");
  t.deepEqual(week(janfirst), "2020W00");
  t.deepEqual(week(date), "2020W11");
  t.deepEqual(quarter(janfirst), "2020Q1");
  t.deepEqual(quarter(date), "2020Q1");
  t.deepEqual(year(janfirst), "2020");
  t.deepEqual(year(date), "2020");
});
