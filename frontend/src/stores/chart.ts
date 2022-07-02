import { derived, writable } from "svelte/store";

import type { NamedChartTypes } from "../charts";
import { _, format } from "../i18n";
import iso4217currencies from "../lib/iso4217";
import { localStorageSyncedStore } from "../lib/store";
import { constant, union } from "../lib/validation";

import { currencies_sorted, operating_currency } from ".";

export const showCharts = writable(true);
export const activeChart = writable<NamedChartTypes | undefined>(undefined);
export const hierarchyChartMode = localStorageSyncedStore<
  "treemap" | "sunburst"
>(
  "hierarchy-chart-mode",
  union(constant("treemap"), constant("sunburst")),
  () => "treemap"
);
export const lineChartMode = localStorageSyncedStore<"line" | "area">(
  "line-chart-mode",
  union(constant("line"), constant("area")),
  () => "line"
);
export const barChartMode = localStorageSyncedStore<"stacked" | "single">(
  "bar-chart-mode",
  union(constant("stacked"), constant("single")),
  () => "stacked"
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
      format(_("Converted to %(currency)s"), { currency }),
    ]),
  ]
);
