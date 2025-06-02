import { getContext, setContext } from "svelte";
import type { Readable } from "svelte/store";
import { derived } from "svelte/store";

import type { AccountTreeNode } from "../charts/hierarchy";
import { is_empty } from "../lib/objects";
import { accounts_set } from "../stores";
import { is_closed_account } from "../stores/accounts";
import {
  show_accounts_with_zero_balance,
  show_accounts_with_zero_transactions,
  show_closed_accounts,
} from "../stores/fava_options";

const key = Symbol("tree-table");

/** The accounts that should not be shown. */
type NotShown = Readable<ReadonlySet<string>>;

export const setTreeTableNotShownContext = (ctx: NotShown): NotShown =>
  setContext(key, ctx);

export const getTreeTableNotShownContext = (): NotShown => getContext(key);

/** Recursively build set of accounts that should not be shown. */
export const get_not_shown = derived(
  [
    show_accounts_with_zero_balance,
    show_accounts_with_zero_transactions,
    show_closed_accounts,
    accounts_set,
    is_closed_account,
  ],
  ([
    $show_accounts_with_zero_balance,
    $show_accounts_with_zero_transactions,
    $show_closed_accounts,
    $accounts_set,
    $is_closed_account,
  ]) =>
    (node: AccountTreeNode, end: Date | null): Set<string> => {
      const not_shown = new Set<string>();
      const should_show_recursive = (n: AccountTreeNode): boolean => {
        if (
          // We need to evaluate this for all descendants recursively
          // the .map().some() ensures it does not short-circuit
          n.children.map(should_show_recursive).some((b) => b) ||
          !is_empty(n.balance_children)
        ) {
          return true;
        }
        if (
          !$accounts_set.has(n.account) ||
          (!$show_closed_accounts && $is_closed_account(n.account, end)) ||
          (!$show_accounts_with_zero_balance && is_empty(n.balance)) ||
          (!$show_accounts_with_zero_transactions && !n.has_txns)
        ) {
          not_shown.add(n.account);
          return false;
        }
        return true;
      };
      should_show_recursive(node);
      return not_shown;
    },
);
