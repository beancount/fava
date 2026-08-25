import { format } from "d3-format";
import type { NumberValue } from "d3-scale";
import { derived } from "svelte/store";

import type { FormatterContext } from "../format.ts";
import {
  formatter_context,
  get_date_format,
  locale_formatter,
  replaceNumbers,
} from "../format.ts";
import { fiscal_year_end, locale } from "./fava_options.ts";
import { incognito, precisions } from "./index.ts";
import { interval } from "./url.ts";

const short_format = format(".3s");

/** Render a number to a short string, for example for the y-axis of a line chart. */
export const short = derived(incognito, ($incognito) =>
  $incognito
    ? (n: NumberValue) => replaceNumbers(short_format(n))
    : short_format,
);

/** Format a number for which the currency is not known. */
export const num = derived(locale, ($locale) => locale_formatter($locale));

/** Formatting context for currencies. */
export const ctx = derived(
  [incognito, locale, precisions],
  ([$incognito, $locale, $precisions]): FormatterContext =>
    formatter_context($incognito, $locale, $precisions),
);

export const date_format = derived(
  [interval, fiscal_year_end],
  ([$interval, $fiscal_year_end]) =>
    get_date_format($interval, $fiscal_year_end),
);
