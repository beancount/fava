import { writable, derived } from "svelte/store";

import { _ } from "../helpers";
import iso4217currencies from "../lib/iso4217";
import { commodities, operating_currency } from ".";

export const showCharts = writable(true);
export const activeChart = writable({});
export const chartMode = writable("treemap");
export const lineChartMode = writable("line");
export const chartCurrency = writable("");

const currencySuggestions = derived(
  [operating_currency, commodities],
  ([operating_currency_val, commodities_val]) => [
    ...operating_currency_val,
    ...commodities_val.filter(
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
