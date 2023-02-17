import { hierarchy as d3Hierarchy } from "d3-hierarchy";
import type { HierarchyNode } from "d3-hierarchy";

import { ok } from "../lib/result";
import type { Result } from "../lib/result";
import type { TreeNode } from "../lib/tree";
import { array, lazy, number, object, record, string } from "../lib/validation";
import type { Validator } from "../lib/validation";

import type { ChartContext } from "./context";

/** The data for a single account in a d3-hierarchy. */
export type AccountHierarchyDatum = TreeNode<{
  account: string;
  balance: Partial<Record<string, number>>;
  dummy?: boolean;
}>;

/** A d3-hierarchy node for an account. */
export type AccountHierarchyNode = HierarchyNode<AccountHierarchyDatum>;

/**
 * Add internal nodes as fake leaf nodes to their own children.
 *
 * In the treemap, we only render leaf nodes, so for accounts that have both
 * children and a balance, we want to duplicate them as leaf nodes.
 */
function addInternalNodesAsLeaves(node: AccountHierarchyDatum): void {
  if (node.children.length) {
    node.children.forEach(addInternalNodesAsLeaves);
    node.children.push({ ...node, children: [], dummy: true });
    node.balance = {};
  }
}

export interface HierarchyChart {
  type: "hierarchy";
  data: Map<string, AccountHierarchyNode>;
}

const account_hierarchy_validator: Validator<AccountHierarchyDatum> = object({
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
      .sum((d) => Math.max((d.balance[currency] ?? 0) * modifier, 0))
      .sort((a, b) => (b.value ?? 0) - (a.value ?? 0));
    if (currencyHierarchy.value) {
      data.set(currency, currencyHierarchy);
    }
  });

  return ok({ type: "hierarchy" as const, data });
}
