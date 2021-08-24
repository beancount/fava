import { hcl } from "d3-color";
import type { HierarchyRectangularNode } from "d3-hierarchy";
import { scaleLinear, scaleOrdinal } from "d3-scale";
import { derived, get } from "svelte/store";

import { currentTimeFilterDateFormat } from "../format";
import { accounts, currencies_sorted, operating_currency } from "../stores";
import { time_filter } from "../stores/filters";
import type { AccountHierarchyDatum } from "../charts";

type SunburstNode = HierarchyRectangularNode<AccountHierarchyDatum>;

/**
 * Set the time filter to the given value (formatted according to the current interval).
 * @param date - a date.
 */
export function setTimeFilter(date: Date): void {
  time_filter.set(get(currentTimeFilterDateFormat)(date));
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
function hclColorRange(count: number, chroma = 45, luminance = 70): string[] {
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
 * The scales for the treemap charts will be initialised with all
 * accounts on page init and currencies with all commodities.
 */
export const scatterplotScale = scaleOrdinal(colors10);

export const treemapScale = derived(accounts, (accounts_val) =>
  scaleOrdinal(colors15).domain(accounts_val)
);

/* Return the colour for the wedge of the sunburst chart representing the given
 * node.  (Note that the root node doesn't get a wedge.)
 *
 * This ensures that adjacent wedges are visually distinct, including the
 * special case of the last and first nodes of the first level.
 * And at other levels, the last child of node A and the first child of node
 * A's sibling are adjacent.
 *
 * Furthermore, these colours try to draw attention to the tree structure
 * underlying the chart.
 */
export function sunburstColor(
  node: SunburstNode,
  root: SunburstNode,
  radius: number
): string {
  const level = node.depth; // 1 is the first level
  const codes = sunburstColorCode(node, root, radius);
  if (codes === null) return hcl(0, 0, 0);

  const [cat_low, cat_high] = COLOR_CATEGORIES[codes[0]];

  let hue;
  if (level == 1) {
    hue = cat_low + (cat_high - cat_low) / 2;
  } else {
    const shadeScale = scaleLinear()
      .domain([0, NUM_SHADES - 1])
      .range([cat_low, cat_high])
      .clamp(true);
    hue = shadeScale(codes[1]);
  }

  // Levels deeper than the second just use the same colour for now.

  return hcl(hue, 35, 80);
}

/* Return an array of indices [a, b, c, ...] for this node.  The last index
 * represents this node; the second-last its parent, third-last its
 * grandparent, etc.  Each index tells how to colour the node within the scope
 * of its parent, as in "choose colour #2".
 * Return null if the node (or any of its ancestors) is not expected to be
 * visible in the chart.
 */
// This is stupidly recursive.  I don't think we have control over the order in
// which node colours are requested, but we should be able to cache this.
function sunburstColorCode(
  node: SunburstNode,
  root: SunburstNode,
  radius: number
): number[] | null {
  // Filter out siblings that won't be shown.  This includes:
  // 1. Dummy nodes: When a non-leaf node has a nonzero balance), it has a
  // "dummy" node child to represent it in the treemap.  In the sunburst chart,
  // dummy nodes are ignored.
  // 2. Slices too narrow to see: The slice width (x1-x0) * 2πr must be at
  // least 2 (to account for 1px borders).  Since this uses the radius of the
  // whole chart, inner levels might still be too narrow to see, but they need
  // to be assigned a colour in case descendant nodes are visible.
  const siblings = node.parent.children.filter(
    n => !n.data.dummy && (n.x1 - n.x0) * (Math.PI * 2 * radius) > 2);
  const index = siblings.indexOf(node);
  const levelWidth = siblings.length;
  const level = node.depth; // 1 is the first level

  if (index == -1) {
    // We don't expect this node to be shown.
    return null;
  }

  if (level == 1) {
    if (levelWidth % COLOR_CATEGORIES.length == 1 && index == levelWidth - 1) {
      return [1];
    }
    return [index % COLOR_CATEGORIES.length];
  } else if (level == 2) {
    const parents = sunburstColorCode(node.parent, root, radius);
    if (parents === null) return null;
    const [level1] = parents;
    if (levelWidth == 1) {
      return [level1, (NUM_SHADES - 1) / 2];
    }
    // TODO: if parent's levelWidth == 1 and this is the last child and its
    // code would be 0, change it to something else.
    return [level1, index % NUM_SHADES];
  } else {
    const parents = sunburstColorCode(node.parent, root, radius);
    if (parents === null) return null;
    return [...parents, index];
  }
}

const COLOR_CATEGORIES = [
  [344, 360+24], // red
  //[63, 74], // yellow -- too narrow
  [100, 144], // green
  //[191, 202], // aqua -- too narrow
  [231, 279], // blue
  [291, 322], // purple
];

const NUM_SHADES = 3;

export const currenciesScale = derived(
  [operating_currency, currencies_sorted],
  ([operating_currency_val, currencies_sorted_val]) =>
    scaleOrdinal(colors10).domain([
      ...operating_currency_val,
      ...currencies_sorted_val,
    ])
);
