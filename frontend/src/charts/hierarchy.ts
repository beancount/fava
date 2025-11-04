import { sum } from "d3-array";
import type { HierarchyNode } from "d3-hierarchy";
import { hierarchy as d3Hierarchy } from "d3-hierarchy";
import type { Writable } from "svelte/store";
import { writable } from "svelte/store";

import type { TreeNode } from "../lib/tree.ts";
import type { Validator } from "../lib/validation.ts";
import {
  array,
  boolean,
  defaultValue,
  lazy,
  number,
  object,
  optional,
  record,
  string,
} from "../lib/validation.ts";
import { sort_by_strings } from "../sort/index.ts";
import type { ChartContext } from "./context.ts";
import type { ParsedFavaChart } from "./index.ts";

/**
 * An account tree - data provided with a fava.core.tree.SerialisedTreeNode.
 *
 * Used in the hierarchy charts but also in e.g. the tree-tables.
 * */
export type AccountTreeNode = TreeNode<{
  readonly account: string;
  readonly balance: Record<string, number>;
  readonly balance_children: Record<string, number>;
  readonly cost: Record<string, number> | null;
  readonly cost_children: Record<string, number> | null;
  readonly has_txns: boolean;
}>;

const sort_children = (values: AccountTreeNode[]) =>
  sort_by_strings(values, (v) => v.account);

const inventory = record(number);

export const account_hierarchy_validator: Validator<AccountTreeNode> = object({
  account: string,
  balance: inventory,
  balance_children: inventory,
  children: lazy(
    () => (json) => array(account_hierarchy_validator)(json).map(sort_children),
  ),
  cost: optional(inventory),
  cost_children: optional(inventory),
  has_txns: defaultValue(boolean, () => false),
});

/** The data for a single account in a d3-hierarchy. */
export type AccountHierarchyDatum = TreeNode<{
  readonly account: string;
  readonly balance: Record<string, number>;
  readonly dummy: boolean;
}>;

type AccountHierarchyInputDatum = TreeNode<{
  readonly account: string;
  readonly balance: Record<string, number>;
}>;

/** A d3-hierarchy node for an account. */
export type AccountHierarchyNode = HierarchyNode<AccountHierarchyDatum>;

/**
 * Add internal nodes as dummy leaf nodes to their own children.
 *
 * In the treemap, we only render leaf nodes, so for accounts that have both
 * children and a balance, we want to duplicate them as leaf nodes.
 */
function add_internal_nodes_as_leaves({
  account,
  balance,
  children,
}: AccountHierarchyInputDatum): AccountHierarchyDatum {
  if (children.length) {
    const c = children.map(add_internal_nodes_as_leaves);
    c.push({ account, balance, children: [], dummy: true });
    return { account, balance: {}, children: c, dummy: false };
  }
  return { account, balance, children: [], dummy: false };
}

export class HierarchyChart {
  readonly type = "hierarchy";
  /** All currencies for which we have an hierarchy. */
  readonly currencies: readonly string[];
  /** The currency to show the treemap of. */
  readonly treemap_currency: Writable<string> | null;
  readonly label: string | null;
  readonly data: ReadonlyMap<string, AccountHierarchyNode>;

  constructor(
    label: string | null,
    data: ReadonlyMap<string, AccountHierarchyNode>,
  ) {
    this.label = label;
    this.data = data;
    this.currencies = [...this.data.keys()];
    const first_currency = this.currencies[0];
    this.treemap_currency =
      first_currency != null ? writable<string>(first_currency) : null;
  }
}

const hierarchy_validator = object({
  label: string,
  data: account_hierarchy_validator,
});

export class ParsedHierarchyChart implements ParsedFavaChart {
  readonly label: string | null;
  readonly data: AccountHierarchyInputDatum;

  constructor(label: string | null, data: AccountHierarchyInputDatum) {
    this.label = label;
    this.data = data;
  }

  static from_node = (node: AccountTreeNode): ParsedHierarchyChart => {
    return new ParsedHierarchyChart(node.account, node);
  };

  static validator: Validator<ParsedHierarchyChart> = (json) =>
    hierarchy_validator(json).map(
      ({ label, data }) => new ParsedHierarchyChart(label, data),
    );

  with_context({ currencies }: ChartContext): HierarchyChart {
    const root = add_internal_nodes_as_leaves(this.data);
    return new HierarchyChart(
      this.label,
      new Map(
        currencies
          .map((currency) => {
            const r = d3Hierarchy<AccountHierarchyDatum>(root);
            const root_balance = sum(
              r.descendants(),
              (n) => n.data.balance[currency] ?? 0,
            );
            // depending on the balance for this currency in the root,
            // build the tree either for all positive values or all negative values
            const sign = root_balance ? Math.sign(root_balance) : 1;
            r.sum(
              (d) => sign * Math.max(sign * (d.balance[currency] ?? 0), 0),
            ).sort((a, b) => sign * ((b.value ?? 0) - (a.value ?? 0)));
            return [currency, r] as const;
          })
          .filter(([, h]) => h.value != null && h.value !== 0),
      ),
    );
  }
}
