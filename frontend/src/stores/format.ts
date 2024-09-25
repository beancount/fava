import { format } from "d3-format";
import { derived } from "svelte/store";

import type { FormatterContext } from "../format";
import { dateFormat, localeFormatter, timeFilterDateFormat } from "../format";
import { incognito, interval, locale, precisions } from ".";

const replaceNumbers = (num: string) => num.replace(/[0-9]/g, "X");

const short_format = format(".3s");

/** Render a number to a short string, for example for the y-axis of a line chart. */
export const short = derived(
  incognito,
  ($incognito): ((number: number | { valueOf(): number }) => string) =>
    $incognito ? (n) => replaceNumbers(short_format(n)) : short_format,
);

/** Format a number for which the currency is not known. */
export const num = derived(locale, ($locale) => localeFormatter($locale));

/** Formatting context for currencies. */
export const ctx = derived(
  [incognito, locale, precisions],
  ([$incognito, $locale, $precisions]): FormatterContext => {
    const formatter = localeFormatter($locale);
    const currencyFormatters = Object.fromEntries(
      Object.entries($precisions).map(([currency, prec]) => [
        currency,
        localeFormatter($locale, prec),
      ]),
    );
    const num_raw = (n: number, c: string) =>
      (currencyFormatters[c] ?? formatter)(n);

    const num = $incognito
      ? (n: number, c: string) => replaceNumbers(num_raw(n, c))
      : num_raw;

    return {
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
