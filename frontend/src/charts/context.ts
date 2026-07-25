import { createContext } from "svelte";
import { derived } from "svelte/store";

import { currentDateFormat } from "../stores/format.ts";
import { currencies } from "../stores/index.ts";
import { operating_currency } from "../stores/options.ts";
import { conversion } from "../stores/url.ts";
import type { Tooltip } from "./tooltip.ts";

/** Context data for parsing and rendering of the charts. */
export interface ChartContext {
  /** The list of operating currencies, complemented by the current conversion currency. */
  readonly currencies: readonly string[];
  /** The current date format as determined from the interval. */
  readonly dateFormat: (date: Date) => string;
}

/**
 * The list of operating currencies, adding in the current conversion currency.
 */
const operatingCurrenciesWithConversion = derived(
  [operating_currency, currencies, conversion],
  ([$operating_currency, $currencies, $conversion]) =>
    $currencies.includes($conversion) &&
    !$operating_currency.includes($conversion)
      ? [...$operating_currency, $conversion]
      : $operating_currency,
);

export const [get_chart_tooltip, set_chart_tooltip] = createContext<Tooltip>();

export const chartContext = derived(
  [operatingCurrenciesWithConversion, currentDateFormat],
  ([$operatingCurrenciesWithConversion, $currentDateFormat]): ChartContext => ({
    currencies: $operatingCurrenciesWithConversion,
    dateFormat: $currentDateFormat,
  }),
);
