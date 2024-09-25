import { sum } from "d3-array";
import type { HierarchyNode } from "d3-hierarchy";
import { hierarchy as d3Hierarchy } from "d3-hierarchy";

import type { Result } from "../lib/result";
import type { TreeNode } from "../lib/tree";
import type { ValidationError, Validator } from "../lib/validation";
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
  unknown,
} from "../lib/validation";
import { notify_warn } from "../notifications";
import type { ChartContext } from "./context";

/** The data provided with a fava.core.tree.SerialisedTreeNode. */
export type AccountTreeNode = TreeNode<{
  readonly account: string;
  readonly balance: Record<string, number>;
  readonly balance_children: Record<string, number>;
  readonly cost: Record<string, number> | null;
  readonly cost_children: Record<string, number> | null;
  readonly has_txns: boolean;
}>;

/** The data for a single account in a d3-hierarchy. */
export type AccountHierarchyDatum = TreeNode<{
  readonly account: string;
  readonly balance: Record<string, number>;
  readonly dummy: boolean;
}>;

export type AccountHierarchyInputDatum = TreeNode<{
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
export function addInternalNodesAsLeaves({
  account,
  balance,
  children,
}: AccountHierarchyInputDatum): AccountHierarchyDatum {
  if (children.length) {
    const c = children.map(addInternalNodesAsLeaves);
    c.push({ account, balance, children: [], dummy: true });
    return { account, balance: {}, children: c, dummy: false };
  }
  return { account, balance, children: [], dummy: false };
}

export class HierarchyChart {
  readonly type = "hierarchy";

  constructor(
    readonly name: string | null,
    readonly data: ReadonlyMap<string, AccountHierarchyNode>,
  ) {}
}

export const account_hierarchy_validator: Validator<AccountTreeNode> = object({
  account: string,
  balance: record(number),
  balance_children: record(number),
  children: lazy(() => array(account_hierarchy_validator)),
  cost: optional(record(number)),
  cost_children: optional(record(number)),
  has_txns: defaultValue(boolean, () => false),
});

export function hierarchy_from_parsed_data(
  label: string | null,
  data: AccountHierarchyInputDatum,
  { currencies }: ChartContext,
): HierarchyChart {
  const root = addInternalNodesAsLeaves(data);
  return new HierarchyChart(
    label,
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
        .filter(([, h]) => h.value),
    ),
  );
}

const hierarchy_data_with_modifier = object({
  modifier: number,
  root: unknown,
});

export function hierarchy(
  label: string | null,
  json: unknown,
  $chartContext: ChartContext,
): Result<HierarchyChart, ValidationError> {
  const with_modifier = hierarchy_data_with_modifier(json);
  if (with_modifier.is_ok) {
    notify_warn(
      "Tree for the hierarchy chart should now be specified at the top-level directly.\n" +
        "{ modifier: 1, root: { ...children } } -> { ...children }",
    );
  }
  const root = with_modifier.is_ok ? with_modifier.value.root : json;
  return account_hierarchy_validator(root).map((r) =>
    hierarchy_from_parsed_data(label, r, $chartContext),
  );
}
