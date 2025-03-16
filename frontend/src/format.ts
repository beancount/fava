/**
 * Helper functions to format numbers and dates.
 */

import { format } from "d3-format";
import { timeFormat, utcFormat } from "d3-time-format";

import type { Interval } from "./lib/interval";

/**
 * A number formatting function for a locale.
 * @param locale - The locale to use.
 * @param precision - The number of decimal digits to show.
 */
export function localeFormatter(
  locale: string | null,
  precision = 2,
): (num: number) => string {
  if (locale == null) {
    return format(`.${precision.toString()}f`);
  }
  // this needs to be between 0 and 20
  const digits = Math.max(0, Math.min(precision, 20));
  const fmt = new Intl.NumberFormat(locale.replace("_", "-"), {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
  return fmt.format.bind(fmt);
}

const formatterPer = format(".2f");
export function formatPercentage(number: number): string {
  return `${formatterPer(Math.abs(number) * 100)}%`;
}

/** Obscure numbers for incognito mode. */
export const replaceNumbers = (num: string): string =>
  num.replace(/[0-9]/g, "X");

export interface FormatterContext {
  /** Render an amount to a string like "2.00 USD". */
  amount: (num: number, currency: string) => string;
  /** Render an number for a currency like "2.00". */
  num: (num: number, currency: string) => string;
}

/** Build the formatter context for the given configuration */
export function formatter_context(
  incognito: boolean,
  locale: string | null,
  precisions: Record<string, number>,
): FormatterContext {
  const formatter = localeFormatter(locale);
  const currencyFormatters = Object.fromEntries(
    Object.entries(precisions).map(([currency, prec]) => [
      currency,
      localeFormatter(locale, prec),
    ]),
  );
  const num_raw = (n: number, c: string) =>
    (currencyFormatters[c] ?? formatter)(n);

  const num = incognito
    ? (n: number, c: string) => replaceNumbers(num_raw(n, c))
    : num_raw;

  return {
    amount: (n, c) => `${num(n, c)} ${c}`,
    num,
  };
}

type DateFormatter = (date: Date) => string;

/** Format the date as a ISO-8601 date string. */
export const day = utcFormat("%Y-%m-%d");

/** Date formatters for human consumption. */
export const dateFormat: Record<Interval, DateFormatter> = {
  year: utcFormat("%Y"),
  quarter: (date) =>
    `${date.getUTCFullYear().toString()}Q${(Math.floor(date.getUTCMonth() / 3) + 1).toString()}`,
  month: utcFormat("%b %Y"),
  week: utcFormat("%GW%V"),
  day,
};

/** Date formatters for the entry filter form. */
export const timeFilterDateFormat: Record<Interval, DateFormatter> = {
  year: utcFormat("%Y"),
  quarter: (date) =>
    `${date.getUTCFullYear().toString()}-Q${(Math.floor(date.getUTCMonth() / 3) + 1).toString()}`,
  month: utcFormat("%Y-%m"),
  week: utcFormat("%G-W%V"),
  day,
};

const local_day = timeFormat("%Y-%m-%d");

/** Today as a ISO-8601 date string. */
export function todayAsString(): string {
  return local_day(new Date());
}
