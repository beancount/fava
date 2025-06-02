import { format } from "d3-format";
import type { NumberValue } from "d3-scale";
import { derived } from "svelte/store";

import type { FormatterContext } from "../format";
import {
  dateFormat,
  formatter_context,
  localeFormatter,
  replaceNumbers,
  timeFilterDateFormat,
} from "../format";
import { incognito, interval, precisions } from ".";
import { locale } from "./fava_options";

const short_format = format(".3s");

/** Render a number to a short string, for example for the y-axis of a line chart. */
export const short = derived(incognito, ($incognito) =>
  $incognito
    ? (n: NumberValue) => replaceNumbers(short_format(n))
    : short_format,
);

/** Format a number for which the currency is not known. */
export const num = derived(locale, ($locale) => localeFormatter($locale));

/** Formatting context for currencies. */
export const ctx = derived(
  [incognito, locale, precisions],
  ([$incognito, $locale, $precisions]): FormatterContext =>
    formatter_context($incognito, $locale, $precisions),
);

export const currentDateFormat = derived(interval, (val) => dateFormat[val]);
export const currentTimeFilterDateFormat = derived(
  interval,
  (val) => timeFilterDateFormat[val],
);
