import { getContext, setContext } from "svelte";
import type { Readable } from "svelte/store";
import { derived } from "svelte/store";

import type { AccountTreeNode } from "../charts/hierarchy";
import { is_empty } from "../lib/objects";
import { accounts, fava_options } from "../stores";
import { is_closed_account } from "../stores/accounts";

const key = Symbol("tree-table");

/** The accounts that should not be shown. */
type NotShown = Readable<ReadonlySet<string>>;

export const setTreeTableNotShownContext = (ctx: NotShown): NotShown =>
  setContext(key, ctx);

export const getTreeTableNotShownContext = (): NotShown => getContext(key);

/** Recursively build set of accounts that should not be shown. */
export const get_not_shown = derived(
  [fava_options, accounts, is_closed_account],
  ([$fava_options, $accounts, $is_closed_account]) =>
    (node: AccountTreeNode, end: Date | null): Set<string> => {
      const {
        show_accounts_with_zero_balance,
        show_accounts_with_zero_transactions,
        show_closed_accounts,
      } = $fava_options;
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
          !$accounts.includes(n.account) ||
          (!show_closed_accounts && $is_closed_account(n.account, end)) ||
          (!show_accounts_with_zero_balance && is_empty(n.balance)) ||
          (!show_accounts_with_zero_transactions && !n.has_txns)
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
