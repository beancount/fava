import { derived, writable } from "svelte/store";

import { NamedChartTypes } from "../charts";
import { _ } from "../i18n";
import iso4217currencies from "../lib/iso4217";
import { localStorageSyncedStore } from "../lib/store";
import { string } from "../lib/validation";

import { currencies_sorted, operating_currency } from ".";

export const showCharts = writable(true);
export const activeChart = writable<NamedChartTypes | undefined>(undefined);
export const hierarchyChartMode = localStorageSyncedStore(
  "hierarchy-chart-mode",
  string,
  () => "treemap"
);
export const lineChartMode = localStorageSyncedStore(
  "line-chart-mode",
  string,
  () => "line"
);
export const chartCurrency = writable("");

const currencySuggestions = derived(
  [operating_currency, currencies_sorted],
  ([operating_currency_val, currencies_sorted_val]) => [
    ...operating_currency_val,
    ...currencies_sorted_val.filter(
      (c) => !operating_currency_val.includes(c) && iso4217currencies.has(c)
    ),
  ]
);

export const conversions = derived(
  currencySuggestions,
  (currencySuggestions_val) => [
    ["at_cost", _("At Cost")],
    ["at_value", _("At Market Value")],
    ["units", _("Units")],
    ...currencySuggestions_val.map((currency) => [
      currency,
      `Converted to ${currency}`,
    ]),
  ]
);
// TODO  _('Converted to %(currency)s', currency=currency)
