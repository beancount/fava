import { derived, writable } from "svelte/store";

import { _, format } from "../i18n";
import iso4217currencies from "../lib/iso4217";
import { localStorageSyncedStore } from "../lib/store";
import { constant, union } from "../lib/validation";

import {
  conversion_currencies,
  currencies_sorted,
  operating_currency,
} from ".";

/** Whether the charts should be shown - this applies globally to all charts. */
export const showCharts = writable(true);
/** This store is used to switch to the same chart (as identified by name) on navigation. */
export const lastActiveChartName = writable<string | undefined>(undefined);
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
  [operating_currency, currencies_sorted, conversion_currencies],
  ([
    operating_currency_val,
    currencies_sorted_val,
    conversion_currencies_val,
  ]) =>
    conversion_currencies_val.length
      ? conversion_currencies_val
      : [
          ...operating_currency_val,
          ...currencies_sorted_val.filter(
            (c) =>
              !operating_currency_val.includes(c) && iso4217currencies.has(c)
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
