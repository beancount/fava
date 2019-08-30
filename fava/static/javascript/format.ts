// Helper functions to format numbers and dates.

import { format } from "d3-format";
import { utcFormat } from "d3-time-format";

import e from "./events";
import { favaAPI, interval } from "./stores";

let formatter: (num: number) => string;
let incognito: (num: string) => string;

e.on("page-init", () => {
  const { locale } = favaAPI.favaOptions;
  if (locale) {
    formatter = new Intl.NumberFormat(locale.replace("_", "-")).format;
  } else {
    formatter = format(".2f");
  }
  if (favaAPI.incognito) {
    incognito = num => num.replace(/[0-9]/g, "X");
  } else {
    incognito = num => num;
  }
});

export function formatCurrency(number: number) {
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

export const dateFormat = {
  year: utcFormat("%Y"),
  quarter(date: Date) {
    return `${date.getUTCFullYear()}Q${Math.floor(date.getUTCMonth() / 3) + 1}`;
  },
  month: utcFormat("%b %Y"),
  week: utcFormat("%YW%W"),
  day: utcFormat("%Y-%m-%d"),
};

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

// eslint-disable-next-line import/no-mutable-exports
export let currentDateFormat = dateFormat.month;
interval.subscribe(intervalValue => {
  currentDateFormat = dateFormat[intervalValue];
});

// eslint-disable-next-line import/no-mutable-exports
export let currentTimeFilterDateFormat = timeFilterDateFormat.month;
interval.subscribe(intervalValue => {
  currentTimeFilterDateFormat = timeFilterDateFormat[intervalValue];
});
