import type { Readable } from "svelte/store";
import { derived } from "svelte/store";

import { currentDateFormat } from "../format";
import { conversion, operating_currency } from "../stores";

export type ChartContext = {
  currencies: string[];
  dateFormat: (date: Date) => string;
};

/**
 * The list of operating currencies, adding in the current conversion currency.
 */
const operatingCurrenciesWithConversion = derived(
  [operating_currency, conversion],
  ([operating_currency_val, conversion_val]) => {
    if (
      !conversion_val ||
      ["at_cost", "at_value", "units"].includes(conversion_val) ||
      operating_currency_val.includes(conversion_val)
    ) {
      return operating_currency_val;
    }
    return [...operating_currency_val, conversion_val];
  }
);

export const chartContext: Readable<ChartContext> = derived(
  [operatingCurrenciesWithConversion, currentDateFormat],
  ([currencies_val, dateFormat]) => ({ currencies: currencies_val, dateFormat })
);
