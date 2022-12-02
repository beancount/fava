import type { Readable } from "svelte/store";
import { derived } from "svelte/store";

import { conversion, currencies, operating_currency } from "../stores";
import { currentDateFormat } from "../stores/format";

export interface ChartContext {
  currencies: string[];
  dateFormat: (date: Date) => string;
}

/**
 * The list of operating currencies, adding in the current conversion currency.
 */
const operatingCurrenciesWithConversion = derived(
  [operating_currency, currencies, conversion],
  ([operating_currency_val, currencies_val, conversion_val]) =>
    currencies_val.includes(conversion_val) &&
    !operating_currency_val.includes(conversion_val)
      ? [...operating_currency_val, conversion_val]
      : operating_currency_val
);

export const chartContext: Readable<ChartContext> = derived(
  [operatingCurrenciesWithConversion, currentDateFormat],
  ([currencies_val, dateFormat]) => ({ currencies: currencies_val, dateFormat })
);
