import { writable, derived } from "svelte/store";

import { _ } from "../helpers";
import { favaAPIStore } from ".";

export const showCharts = writable(true);
export const activeChart = writable({});
export const chartMode = writable("treemap");
export const chartCurrency = writable("");

export const conversions = derived(favaAPIStore, favaAPI => [
  ["at_cost", _("At Cost")],
  ["at_value", _("At Market Value")],
  ["units", _("Units")],
  ...favaAPI.options.operating_currency
    .sort()
    .map(currency => [currency, `Converted to ${currency}`]),
  ...favaAPI.options.commodities
    .sort()
    .filter(
      c => !favaAPI.options.operating_currency.includes(c) && c.length <= 3
    )
    .map(currency => [currency, `Converted to ${currency}`]),
]);
// TODO  _('Converted to %(currency)s', currency=currency)
