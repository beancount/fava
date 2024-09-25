import { derived, writable } from "svelte/store";

import { _ } from "../i18n";
import iso4217currencies from "../lib/iso4217";
import { localStorageSyncedStore } from "../lib/store";
import type { ValidationT } from "../lib/validation";
import { array, constants, string } from "../lib/validation";
import {
  conversion_currencies,
  currencies_sorted,
  operating_currency,
} from ".";

/** Whether the charts should be shown - this applies globally to all charts. */
export const showCharts = writable(true);

/** This store is used to switch to the same chart (as identified by name) on navigation. */
export const lastActiveChartName = writable<string | null>(null);

const hierarchy_chart_mode_validator = constants("treemap", "sunburst");
type HierarchyChartMode = ValidationT<typeof hierarchy_chart_mode_validator>;

/** The currently selected hierarchy chart mode. */
export const hierarchyChartMode = localStorageSyncedStore<HierarchyChartMode>(
  "hierarchy-chart-mode",
  hierarchy_chart_mode_validator,
  () => "treemap",
  () => [
    ["treemap", _("Treemap")],
    ["sunburst", _("Sunburst")],
  ],
);

const line_chart_mode_validator = constants("line", "area");
type LineChartMode = ValidationT<typeof line_chart_mode_validator>;

/** The currently selected line chart mode. */
export const lineChartMode = localStorageSyncedStore<LineChartMode>(
  "line-chart-mode",
  line_chart_mode_validator,
  () => "line",
  () => [
    ["line", _("Line chart")],
    ["area", _("Area chart")],
  ],
);

const bar_chart_mode_validator = constants("stacked", "single");
type BarChartMode = ValidationT<typeof bar_chart_mode_validator>;

/** The currently selected bar chart mode. */
export const barChartMode = localStorageSyncedStore<BarChartMode>(
  "bar-chart-mode",
  bar_chart_mode_validator,
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
