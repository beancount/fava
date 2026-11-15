import { createContext } from "svelte";
import { derived } from "svelte/store";

import type { FiscalYearEnd } from "../lib/interval.ts";
import { fiscal_year_end } from "../stores/fava_options.ts";
import { currencies } from "../stores/index.ts";
import { operating_currency } from "../stores/options.ts";
import { conversion } from "../stores/url.ts";
import type { Tooltip } from "./tooltip.ts";

/** Context data for parsing and rendering of the charts. */
export interface ChartContext {
  /** The list of operating currencies, complemented by the current conversion currency. */
  readonly currencies: readonly string[];
  /** The fiscal year end, to format dates for fiscal intervals. */
  readonly fiscal_year_end: FiscalYearEnd;
}

/**
 * The list of operating currencies, adding in the current conversion currency.
 */
const operating_currencies_with_conversion = derived(
  [operating_currency, currencies, conversion],
  ([$operating_currency, $currencies, $conversion]) =>
    $currencies.includes($conversion) &&
    !$operating_currency.includes($conversion)
      ? [...$operating_currency, $conversion]
      : $operating_currency,
);

export const [get_chart_tooltip, set_chart_tooltip] = createContext<Tooltip>();

export const chart_context = derived(
  [operating_currencies_with_conversion, fiscal_year_end],
  ([
    $operating_currencies_with_conversion,
    $fiscal_year_end,
  ]): ChartContext => ({
    currencies: $operating_currencies_with_conversion,
    fiscal_year_end: $fiscal_year_end,
  }),
);
