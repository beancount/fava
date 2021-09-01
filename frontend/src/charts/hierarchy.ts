import { hcl } from "d3-color";
import type { Color } from "d3-color";
import {
    hierarchy as d3Hierarchy,
    partition,
} from "d3-hierarchy";
import type { HierarchyNode, HierarchyRectangularNode } from "d3-hierarchy";
import { scaleLinear } from "d3-scale";

import { ok } from "../lib/result";
import type { Result } from "../lib/result";
import type { TreeNode } from "../lib/tree";
import { array, lazy, number, object, record, string } from "../lib/validation";
import type { Validator } from "../lib/validation";

import type { ChartContext } from "./context";

export interface AccountHierarchyDatum {
  account: string;
  balance: Partial<Record<string, number>>;
  dummy?: boolean;
}
type RawAccountHierarchy = TreeNode<AccountHierarchyDatum>;
export type AccountHierarchyNode = HierarchyNode<AccountHierarchyDatum>;
/**
 * Add internal nodes as fake leaf nodes to their own children.
 *
 * In the treemap, we only render leaf nodes, so for accounts that have both
 * children and a balance, we want to duplicate them as leaf nodes.
 */
function addInternalNodesAsLeaves(node: RawAccountHierarchy): void {
  if (node.children.length) {
    node.children.forEach(addInternalNodesAsLeaves);
    node.children.push({ ...node, children: [], dummy: true });
    node.balance = {};
  }
}

export interface HierarchyChart {
  type: "hierarchy";
  data: Map<string, AccountHierarchyNode>;
  tooltipText?: undefined;
}

const account_hierarchy_validator: Validator<RawAccountHierarchy> = object({
  account: string,
  balance: record(number),
  children: lazy(() => array(account_hierarchy_validator)),
});
const hierarchy_validator = object({
  root: account_hierarchy_validator,
  modifier: number,
});

export function hierarchy(
  json: unknown,
  { currencies }: ChartContext
): Result<HierarchyChart, string> {
  const res = hierarchy_validator(json);
  if (!res.success) {
    return res;
  }
  const { root, modifier } = res.value;
  addInternalNodesAsLeaves(root);
  const data = new Map<string, AccountHierarchyNode>();

  currencies.forEach((currency) => {
    const currencyHierarchy = d3Hierarchy(root)
      .sum((d) => (d.balance[currency] ?? 0) * modifier)
      .sort((a, b) => (b.value ?? 0) - (a.value ?? 0));
    currencyHierarchy.sign = modifier;
    if (currencyHierarchy.value) {
      data.set(currency, currencyHierarchy);
    }
  });

  return ok({ type: "hierarchy" as const, data });
}

/* Sunburst chart helpers */

/* First-level wedges are assigned a colour category from this list.
 * Each entry is a [min, max] range of HCL hues.  The colour chosen will be the
 * midpoint of the range, but second-level colours will be shades chosen from
 * the range.
 */
const COLOR_CATEGORIES = [
  [344, 360+24], // red
  // [63, 74], // yellow -- too narrow for multiple shades
  [100, 144], // green
  // [191, 202], // aqua -- too narrow for multiple shades
  [231, 279], // blue
  [291, 322], // purple
];

/* Each second-level wedge is assigned a colour from within the colour category
 * of its parent wedge.  The hue range is divided into NUM_SHADES choices.
 */
const NUM_SHADES = 3;

/* This is the minimum width in pixels, measured at the inner diameter of the
 * sunburst chart, of a slice.  Slices smaller than this are grouped into an
 * "other" slice, so only the "other" slice may be smaller than this minimum.
 * The width here is the mathematical size of the shape, and does not take any
 * border-width into account.
 */
const SUNBURST_MIN_SLICE_WIDTH = 3;

interface SunburstNode extends HierarchyRectangularNode<AccountHierarchyDatum> {
  colorIndex: number,
  color: Color,
}

/* Return a 0-based index representing the colour to give the sunburst wedge
 * for this tree node.  The actual colours are looked up by sunburstColor using
 * the index for the node and its ancestors.
 *
 * The caller should assign the result to node.colorIndex, and must ensure that
 * colorIndex has been set for all this nodes' ancestors.
 *
 * This ensures that adjacent wedges are visually distinct, including the
 * special case at the top of the circle where the first and last wedges are
 * adjacent.  Furthermore, these colours try to draw attention to the tree
 * structure underlying the chart.
 */
function sunburstColorIndex(node: SunburstNode): number {
  // Level width does not include the "other" entry (if present) because it is
  // coloured distinctly and may be invisibly narrow or nearly so.
  function getLevelWidth(n: SunburstNode): number {
    const nodes = n.parent.children;
    if (nodes[nodes.length - 1].data.isOther) {
      return nodes.length - 1;
    }
    return nodes.length;
  }

  if (node.data.isOther) {
    return -1;
  }

  const siblings = node.parent.children;
  const index = siblings.indexOf(node);
  const levelWidth = getLevelWidth(node);
  const level = node.depth; // 1 is the first level

  if (level === 1) {
    if (levelWidth % COLOR_CATEGORIES.length === 1
        && index === levelWidth - 1) {
      return 1;
    }
    return index % COLOR_CATEGORIES.length;
  }

  if (level === 2) {
    let rv;
    if (levelWidth === 1) {
      rv = (NUM_SHADES - 1) / 2;
    } else {
      rv = index % NUM_SHADES;
    }

    // Normally at the second level, the first slice and the last slice cannot
    // have the same colour because their parents (first-level slices) have
    // different colours.  However, if there is only one first-level slice
    // shown, then the first and last second-level slices have the same parent
    // and thus the same base colour and are in danger of being assinged the
    // same shade.
    const parentLevelWidth = getLevelWidth(node.parent);
    if (parentLevelWidth === 1
        && index === levelWidth - 1 // this is the last child
        && rv === 0) { // it was to be assigned colour 0 (same as first child)
      rv = 1;
    }

    return rv;
  }

  return index;
}

/* Return the colour for the wedge of the sunburst chart representing the given
 * node.  (Note that the root node doesn't get a wedge.)
 */
function sunburstColor(node: SunburstNode): Color {
  if (node.data.isOther) {
    return hcl(0, 0, 80);
  }

  const indices = [];
  for (const n = node; n.parent; n = n.parent) {
    indices.unshift(n.colorIndex);
  }
  // assert: node.depth === indices.length

  const level = node.depth;
  const [cat_low, cat_high] = COLOR_CATEGORIES[indices[0]];

  let hue;
  if (level === 1) {
    hue = cat_low + (cat_high - cat_low) / 2;
  } else {
    const shadeScale = scaleLinear()
      .domain([0, NUM_SHADES - 1])
      .range([cat_low, cat_high])
      .clamp(true);
    hue = shadeScale(indices[1]);
  }

  // Levels deeper than the second just use the same colour for now.

  return hcl(hue, 35, 80);
}

/* Produce a tree of SunburstNodes of what the sunburst chart should show.
 *
 * - Collapses nodes that will be too small into a single "other" node for each
 *   set of siblings.
 * - Assigns colours to nodes.
 *
 * d3-hierarchy has no facility for modifying a tree after hierarchy() is
 * called, so this has to construct a temporary Partition, inspect it, and then
 * construct a new hierarchy of just the parts to keep.
 */
export function sunburstTree(
  orig_data: AccountHierarchyNode & { sign: number },
  radius: number,
  currency: string,
  y: (number) => number, // y = scaleSqrt from Sunburst.svelte
): SunburstNode {

  const { sign } = orig_data;
  // assert: sign === 1 || sign === -1

  let data = partition<AccountHierarchyDatum>()(orig_data);
  const inner_radius = y(data.y1);

  // Mark nodes that won't be shown.
  data.each(n => {
    if (n.depth === 0) {
      // Always ignore the root node.
    }

    // Dummy nodes: When a non-leaf node has a nonzero balance), it has a
    // "dummy" node child to represent it in the treemap.  In the sunburst
    // chart, dummy nodes are ignored.
    else if (n.data.dummy) {
      n.del = true;
    }

    else if (n.value === 0) {
      n.del = true;
    }

    // Negative balances: Accounts with negative balances can't be represented,
    // but we must also omit their sibling accounts because the proportions
    // will misrepresent the accounts, and, except at the first level, the sum
    // of the child account sizes may exceed the parent's size.  At the first
    // level, siblings are not omitted because that would leave an empty chart.
    else if (n.value < 0) {
      n.del = true;
      if (n.depth > 1) {
        for (const sibling of n.parent.children) {
          sibling.del = true;
        }
      }
    }

    // Slices too narrow to see: The slice width (x1-x0) * 2πr must be at
    // least SUNBURST_MIN_SLICE_WIDTH.  Compare the width using the inner
    // radius of the chart to avoid visible descendants of invisible slices.
    else if ((n.x1 - n.x0) * Math.PI * 2 * inner_radius
        < SUNBURST_MIN_SLICE_WIDTH) {
      n.del = true;
      if (!n.parent.other_children) {
        n.parent.other_children = 0;
      }
      n.parent.other_children += n.value;
    }
  });

  interface TempNode extends HierarchyRectangularNode<AccountHierarchyDatum> {
    del?: boolean;
  }
  function toSunburstData(n: TempNode): RawAccountHierarchy {
    if (n.del) {
      return null;
    }
    let children = [];
    if (n.children) {
      children = n.children.map(toSunburstData).filter(x => x !== null);
    }
    if (n.other_children) {
      children.push({
        account: "(other)",
        balance: { [currency]: n.other_children * sign },
        isOther: true,
      });
    }
    return {
      account: n.data.account,
      balance: n.data.balance,
      children,
    };
  }

  data = d3Hierarchy(toSunburstData(data))
    .sum((d) => d.balance[currency] * sign)
    .sort((a, b) => {
      // Always sort the "other" entry last, regardless of its size.
      if (a.data.isOther) { return 1; }
      if (b.data.isOther) { return -1; }
      return b.value - a.value
    });

  data = partition<AccountHierarchyDatum>()(data);

  data.eachBefore(n => {
    if (n.parent) {
      n.colorIndex = sunburstColorIndex(n);
      n.color = sunburstColor(n);
    }
  });

  return data;
}
