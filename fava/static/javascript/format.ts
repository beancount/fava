/**
 * Helper functions to format numbers and dates.
 */

import { format } from "d3-format";
import { utcFormat, timeFormat } from "d3-time-format";
import { derived } from "svelte/store";

import { favaAPIStore, interval } from "./stores";

let formatter: (num: number) => string;
let incognito: (num: string) => string;

favaAPIStore.subscribe(favaAPI => {
  const { locale } = favaAPI.favaOptions;
  formatter = locale
    ? new Intl.NumberFormat(locale.replace("_", "-")).format
    : (formatter = format(".2f"));
  incognito = favaAPI.incognito
    ? num => num.replace(/[0-9]/g, "X")
    : num => num;
});

export function formatCurrency(number: number): string {
  return incognito(formatter(number));
}

const formatterPer = format(".2f");
export function formatPercentage(number: number) {
  return `${formatterPer(Math.abs(number) * 100)}%`;
}

const formatterShort = format(".2s");
export function formatCurrencyShort(number: number) {
  return incognito(formatterShort(number));
}

/** Date formatters for human consumption. */
export const dateFormat = {
  year: utcFormat("%Y"),
  quarter(date: Date) {
    return `${date.getUTCFullYear()}Q${Math.floor(date.getUTCMonth() / 3) + 1}`;
  },
  month: utcFormat("%b %Y"),
  week: utcFormat("%YW%W"),
  day: utcFormat("%Y-%m-%d"),
};

/** Date formatters for the entry filter form. */
export const timeFilterDateFormat = {
  year: utcFormat("%Y"),
  quarter(date: Date) {
    return `${date.getUTCFullYear()}-Q${Math.floor(date.getUTCMonth() / 3) +
      1}`;
  },
  month: utcFormat("%Y-%m"),
  week: utcFormat("%Y-W%W"),
  day: utcFormat("%Y-%m-%d"),
};

/** Today as a ISO-8601 date string. */
export function todayAsString(): string {
  return timeFormat("%Y-%m-%d")(new Date());
}
export const currentDateFormat = derived(interval, val => dateFormat[val]);
export const currentTimeFilterDateFormat = derived(
  interval,
  val => timeFilterDateFormat[val]
);
