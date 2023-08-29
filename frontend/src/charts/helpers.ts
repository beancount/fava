import { hcl } from "d3-color";
import { scaleOrdinal } from "d3-scale";
import { derived, get as store_get } from "svelte/store";

import { accounts, currencies_sorted, operating_currency } from "../stores";
import { currentTimeFilterDateFormat } from "../stores/format";

/**
 * Set the time filter to the given value (formatted according to the current interval).
 * @param date - a date.
 * @returns A URL for the given interval.
 */
export function urlForTimeFilter(date: Date): string {
  const url = new URL(window.location.href);
  url.searchParams.set("time", store_get(currentTimeFilterDateFormat)(date));
  return url.toString();
}

/**
 * Include zero in the extent.
 *
 * For convenience this also turns a empty extent into [0,1].
 */
export function includeZero([from, to]:
  | [number, number]
  | [undefined, undefined]): [number, number] {
  if (from === undefined) {
    return [0, 1];
  }
  return [Math.min(0, from), Math.max(0, to)];
}

/**
 * Pad the extent by a factor of 0.05.
 *
 * For convenience this also turns a empty extent into [0,1].
 */
export function padExtent([from, to]:
  | [number, number]
  | [undefined, undefined]): [number, number] {
  if (from === undefined) {
    return [0, 1];
  }
  const diff = to - from;
  return [from - diff * 0.03, to + diff * 0.03];
}

/**
 * Filter ticks to have them not overlap.
 * @param domain - The domain of values to filter.
 * @param count - The number of ticks that should be returned.
 */
export function filterTicks(domain: string[], count: number): string[] {
  if (domain.length <= count) {
    return domain;
  }
  const showIndices = Math.ceil(domain.length / count);
  return domain.filter((d, i) => i % showIndices === 0);
}

/**
 * Generate an array of colors.
 *
 * Uses the HCL color space in an attempt to generate colours that are
 * to be perceived to be of the same brightness.
 * @param count - the number of colors to generate.
 * @param chroma - optional, the chroma channel value.
 * @param luminance - optional, the luminance channel value.
 */
export function hclColorRange(
  count: number,
  chroma = 45,
  luminance = 70,
): string[] {
  const offset = 270;
  const delta = 360 / count;
  const colors = [...Array(count).keys()].map((index) => {
    const hue = (index * delta + offset) % 360;
    return hcl(hue, chroma, luminance);
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

export const treemapScale = derived(accounts, ($accounts) =>
  scaleOrdinal(colors15).domain($accounts),
);

export const sunburstScale = derived(accounts, ($accounts) =>
  scaleOrdinal(colors10).domain($accounts),
);

export const currenciesScale = derived(
  [operating_currency, currencies_sorted],
  ([$operating_currency, $currencies_sorted]) =>
    scaleOrdinal(colors10).domain([
      ...$operating_currency,
      ...$currencies_sorted,
    ]),
);
