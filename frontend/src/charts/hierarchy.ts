import { hierarchy as d3Hierarchy } from "d3-hierarchy";
import type { HierarchyNode } from "d3-hierarchy";

import type { Result } from "../lib/result";
import type { TreeNode } from "../lib/tree";
import {
  array,
  boolean,
  lazy,
  number,
  object,
  optional,
  record,
  string,
} from "../lib/validation";
import type { Validator } from "../lib/validation";

import type { ChartContext } from "./context";

/** The data provided with a fava.core.tree.SerialisedTreeNode. */
export type AccountTreeNode = TreeNode<{
  account: string;
  balance: Record<string, number>;
  balance_children: Record<string, number>;
  cost: Record<string, number> | null;
  cost_children: Record<string, number> | null;
  has_txns: boolean;
}>;

/** The data for a single account in a d3-hierarchy. */
export type AccountHierarchyDatum = TreeNode<{
  account: string;
  balance: Record<string, number>;
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

export class HierarchyChart {
  readonly type = "hierarchy";

  constructor(
    readonly name: string | null,
    readonly data: Map<string, AccountHierarchyNode>,
  ) {}
}

export const account_hierarchy_validator: Validator<AccountTreeNode> = object({
  account: string,
  balance: record(number),
  balance_children: record(number),
  children: lazy(() => array(account_hierarchy_validator)),
  cost: optional(record(number)),
  cost_children: optional(record(number)),
  has_txns: boolean,
});

const hierarchy_validator = object({
  root: account_hierarchy_validator,
  modifier: number,
});

export function hierarchy(
  label: string | null,
  json: unknown,
  { currencies }: ChartContext,
): Result<HierarchyChart, string> {
  return hierarchy_validator(json).map((value) => {
    const { root, modifier } = value;
    addInternalNodesAsLeaves(root);
    const data = new Map<string, AccountHierarchyNode>();

    currencies.forEach((currency) => {
      const currencyHierarchy = d3Hierarchy<AccountHierarchyDatum>(root)
        .sum((d) => Math.max((d.balance[currency] ?? 0) * modifier, 0))
        .sort((a, b) => (b.value ?? 0) - (a.value ?? 0));
      if (currencyHierarchy.value) {
        data.set(currency, currencyHierarchy);
      }
    });

    return new HierarchyChart(label, data);
  });
}
