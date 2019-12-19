import { hcl } from "d3-color";
import { scaleOrdinal } from "d3-scale";
import { get } from "svelte/store";

import { filters } from "../stores";
import { currentTimeFilterDateFormat } from "../format";

export const NO_MARGINS = {
  top: 0,
  right: 0,
  bottom: 0,
  left: 0,
};

export function setTimeFilter(date: Date) {
  filters.update(fs => ({
    ...fs,
    time: get(currentTimeFilterDateFormat)(date),
  }));
}

/*
 * Generate an array of colors.
 *
 * Uses the HCL color space in an attempt to generate colours that are
 * to be perceived to be of the same brightness.
 */
function hclColorRange(count: number, chroma = 45, lightness = 70) {
  const offset = 270;
  const delta = 360 / count;
  const colors = [...Array(count).keys()].map(index => {
    const hue = (index * delta + offset) % 360;
    return hcl(hue, chroma, lightness);
  });
  return colors;
}

const colors10 = hclColorRange(10).map(c => c.toString());
const colors15 = hclColorRange(15, 30, 80).map(c => c.toString());

/*
 * The color scales for the charts.
 *
 * The scales for treemap and sunburst charts will be initialised with all
 * accounts on page init and currencies with all commodities.
 */
export const scales = {
  treemap: scaleOrdinal(colors15),
  sunburst: scaleOrdinal(colors10),
  currencies: scaleOrdinal(colors10),
  scatterplot: scaleOrdinal(colors10),
};
