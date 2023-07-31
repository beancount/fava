import { format } from "d3-format";
import { derived } from "svelte/store";

import type { FormatterContext } from "../format";
import { dateFormat, localeFormatter, timeFilterDateFormat } from "../format";

import { fava_options, incognito, interval, precisions } from ".";

const replaceNumbers = (num: string) => num.replace(/[0-9]/g, "X");

const formatterShort = format(".3s");

export const ctx = derived(
  [incognito, fava_options, precisions],
  ([i, f, p]): FormatterContext => {
    const formatter = localeFormatter(f.locale);
    const currencyFormatters = Object.fromEntries(
      Object.entries(p).map(([currency, prec]) => [
        currency,
        localeFormatter(f.locale, prec),
      ]),
    );
    const num = (n: number, c: string) => {
      const currencyFormatter = currencyFormatters[c];
      return currencyFormatter ? currencyFormatter(n) : formatter(n);
    };
    return i
      ? {
          short: (n) => replaceNumbers(formatterShort(n)),
          amount: (n, c) => `${replaceNumbers(formatter(n))} ${c}`,
          num: (n) => replaceNumbers(formatter(n)),
        }
      : {
          short: (n) => formatterShort(n),
          amount: (n, c) => `${num(n, c)} ${c}`,
          num,
        };
  },
);

export const currentDateFormat = derived(interval, (val) => dateFormat[val]);
export const currentTimeFilterDateFormat = derived(
  interval,
  (val) => timeFilterDateFormat[val],
);
