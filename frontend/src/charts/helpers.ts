import { hcl } from "d3-color";
import { scaleOrdinal } from "d3-scale";
import { get, derived } from "svelte/store";

import { accounts, operating_currency, currencies_sorted } from "../stores";
import { time_filter } from "../stores/filters";
import { currentTimeFilterDateFormat } from "../format";

export function setTimeFilter(date: Date): void {
  time_filter.set(get(currentTimeFilterDateFormat)(date));
}

/*
 * Generate an array of colors.
 *
 * Uses the HCL color space in an attempt to generate colours that are
 * to be perceived to be of the same brightness.
 */
function hclColorRange(count: number, chroma = 45, lightness = 70): string[] {
  const offset = 270;
  const delta = 360 / count;
  const colors = [...Array(count).keys()].map((index) => {
    const hue = (index * delta + offset) % 360;
    return hcl(hue, chroma, lightness);
  });
  return colors.map((c) => c.toString());
}

export const colors10 = hclColorRange(10);
export const colors15 = hclColorRange(15, 30, 80);

/*
 * The color scales for the charts.
 *
 * The scales for treemap and sunburst charts will be initialised with all
 * accounts on page init and currencies with all commodities.
 */
export const scatterplotScale = scaleOrdinal(colors10);

export const treemapScale = derived(accounts, (accounts_val) =>
  scaleOrdinal(colors15).domain(accounts_val)
);

export const sunburstScale = derived(accounts, (accounts_val) =>
  scaleOrdinal(colors10).domain(accounts_val)
);

export const currenciesScale = derived(
  [operating_currency, currencies_sorted],
  ([operating_currency_val, currencies_sorted_val]) =>
    scaleOrdinal(colors10).domain([
      ...operating_currency_val,
      ...currencies_sorted_val,
    ])
);
