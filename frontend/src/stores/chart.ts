import { derived, writable } from "svelte/store";

import { _ } from "../i18n";
import iso4217currencies from "../lib/iso4217";
import { localStorageSyncedStore } from "../lib/store";
import { array, constant, string, union } from "../lib/validation";

import {
  conversion_currencies,
  currencies_sorted,
  operating_currency,
} from ".";

/** Whether the charts should be shown - this applies globally to all charts. */
export const showCharts = writable(true);

/** This store is used to switch to the same chart (as identified by name) on navigation. */
export const lastActiveChartName = writable<string | null>(null);

/** The currently selected hierarchy chart mode. */
export const hierarchyChartMode = localStorageSyncedStore<
  "treemap" | "sunburst"
>(
  "hierarchy-chart-mode",
  union(constant("treemap"), constant("sunburst")),
  () => "treemap",
  () => [
    ["treemap", _("Treemap")],
    ["sunburst", _("Sunburst")],
  ],
);

/** The currently selected line chart mode. */
export const lineChartMode = localStorageSyncedStore<"line" | "area">(
  "line-chart-mode",
  union(constant("line"), constant("area")),
  () => "line",
  () => [
    ["line", _("Line chart")],
    ["area", _("Area chart")],
  ],
);

/** The currently selected bar chart mode. */
export const barChartMode = localStorageSyncedStore<"stacked" | "single">(
  "bar-chart-mode",
  union(constant("stacked"), constant("single")),
  () => "stacked",
  () => [
    ["stacked", _("Stacked Bars")],
    ["single", _("Single Bars")],
  ],
);

/** The currencies that are currently not shown in the bar and line charts. */
export const chartToggledCurrencies = localStorageSyncedStore(
  "chart-toggled-currencies",
  array(string),
  () => [],
);

/** The currency to show the treemap of. */
export const treemapCurrency = writable<string | null>(null);

/** The currencies to over as conversion options. */
const currency_suggestions = derived(
  [operating_currency, currencies_sorted, conversion_currencies],
  ([$operating_currency, $currencies_sorted, $conversion_currencies]) =>
    $conversion_currencies.length > 0
      ? $conversion_currencies
      : [
          ...$operating_currency,
          ...$currencies_sorted.filter(
            (c) => !$operating_currency.includes(c) && iso4217currencies.has(c),
          ),
        ],
);

/** The possible conversion options and their human-readable descriptions. */
export const conversions = derived(
  currency_suggestions,
  ($currency_suggestions): readonly string[] => [
    "at_cost",
    "at_value",
    "units",
    ...$currency_suggestions,
  ],
);
