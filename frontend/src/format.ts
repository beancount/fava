/**
 * Helper functions to format numbers and dates.
 */

import { format } from "d3-format";
import { timeFormat, utcFormat } from "d3-time-format";
import { derived } from "svelte/store";

import { favaAPIStore, interval } from "./stores";

let formatter: (num: number) => string;
let incognito: (num: string) => string;

/**
 * A number formatting function for a locale.
 * @param locale - The locale to use.
 */
export function localeFormatter(
  locale: string | null
): (num: number) => string {
  if (!locale) {
    return format(".2f");
  }
  const opts = {
    minimumFractionDigits: 2,
  };
  const fmt = new Intl.NumberFormat(locale.replace("_", "-"), opts);
  return fmt.format.bind(fmt);
}

favaAPIStore.subscribe((favaAPI) => {
  const { locale } = favaAPI.favaOptions;
  formatter = localeFormatter(locale);
  incognito = favaAPI.incognito
    ? (num: string): string => num.replace(/[0-9]/g, "X")
    : (num: string): string => num;
});

export function formatCurrency(number: number): string {
  return incognito(formatter(number));
}

const formatterPer = format(".2f");
export function formatPercentage(number: number): string {
  return `${formatterPer(Math.abs(number) * 100)}%`;
}

const formatterShort = format(".3s");
export function formatCurrencyShort(
  number: number | { valueOf(): number }
): string {
  return incognito(formatterShort(number));
}

type DateFormatter = (date: Date) => string;
interface DateFormatters {
  year: DateFormatter;
  quarter: DateFormatter;
  month: DateFormatter;
  week: DateFormatter;
  day: DateFormatter;
}

/** Date formatters for human consumption. */
export const dateFormat: DateFormatters = {
  year: utcFormat("%Y"),
  quarter: (date: Date): string =>
    `${date.getUTCFullYear()}Q${Math.floor(date.getUTCMonth() / 3) + 1}`,
  month: utcFormat("%b %Y"),
  week: utcFormat("%YW%W"),
  day: utcFormat("%Y-%m-%d"),
};

/** Date formatters for the entry filter form. */
export const timeFilterDateFormat: DateFormatters = {
  year: utcFormat("%Y"),
  quarter: (date: Date): string =>
    `${date.getUTCFullYear()}-Q${Math.floor(date.getUTCMonth() / 3) + 1}`,
  month: utcFormat("%Y-%m"),
  week: utcFormat("%Y-W%W"),
  day: utcFormat("%Y-%m-%d"),
};

/** Today as a ISO-8601 date string. */
export function todayAsString(): string {
  return timeFormat("%Y-%m-%d")(new Date());
}
export const currentDateFormat = derived(interval, (val) => dateFormat[val]);
export const currentTimeFilterDateFormat = derived(
  interval,
  (val) => timeFilterDateFormat[val]
);
