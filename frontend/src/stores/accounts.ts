import type { Readable } from "svelte/store";
import { derived, get as store_get, writable } from "svelte/store";

import { _ } from "../i18n";
import { is_descendant, is_descendant_or_equal, parent } from "../lib/account";
import { account_details, accounts_internal } from ".";
import {
  collapse_pattern,
  invert_income_liabilities_equity,
} from "./fava_options";
import { name_equity, name_income, name_liabilities } from "./options";

/** The accounts that are toggled via the collapse-pattern option. */
const collapsed_accounts: Readable<readonly string[]> = derived(
  [collapse_pattern, accounts_internal],
  ([$collapse_pattern, $accounts_internal]) => {
    const matchers = $collapse_pattern.map((pattern) => new RegExp(pattern));
    return $accounts_internal.filter((account: string) =>
      matchers.some((matcher) => matcher.test(account)),
    );
  },
);

// The accounts that were manually toggled.
// `true` stands for 'toggled' and `false` for 'open'.
const explicitly_toggled = writable<ReadonlyMap<string, boolean>>(new Map());

/** The accounts that are toggled in trees. */
export const toggled_accounts: Readable<ReadonlySet<string>> = derived(
  [collapsed_accounts, explicitly_toggled],
  ([$collapsed_accounts, $explicitly_toggled]) => {
    const toggled = new Set($collapsed_accounts);
    for (const [account, is_toggled] of $explicitly_toggled) {
      if (is_toggled) {
        toggled.add(account);
      } else {
        toggled.delete(account);
      }
    }
    return toggled;
  },
);

/**
 * Toggle an account.
 *
 * If opening and it is a Shift-Click, deeply open all descendants.
 * If opening and it is a Ctrl- or Meta-Click, open direct children.
 */
export function toggle_account(account: string, event: MouseEvent): void {
  const $toggled_accounts = store_get(toggled_accounts);
  const $accounts_internal = store_get(accounts_internal);
  const is_opening = $toggled_accounts.has(account);

  explicitly_toggled.update(($explicitly_toggled) => {
    const new_explicitly_toggled = new Map($explicitly_toggled);
    new_explicitly_toggled.set(account, !is_opening);
    if (is_opening) {
      if (event.shiftKey) {
        $accounts_internal.filter(is_descendant(account)).forEach((child) => {
          new_explicitly_toggled.set(child, false);
        });
      } else if (event.ctrlKey || event.metaKey) {
        $accounts_internal
          .filter((a) => parent(a) === account)
          .forEach((child) => {
            new_explicitly_toggled.set(child, true);
          });
      }
    }
    return new_explicitly_toggled;
  });
}

/** Deeply expand all children of the account. */
export function expand_all(account: string): void {
  const $toggled_accounts = store_get(toggled_accounts);

  explicitly_toggled.update(($explicitly_toggled) => {
    const new_explicitly_toggled = new Map($explicitly_toggled);
    [...$toggled_accounts]
      .filter(is_descendant_or_equal(account))
      .forEach((descendant) => {
        new_explicitly_toggled.set(descendant, false);
      });
    return new_explicitly_toggled;
  });
}

/** Whether the balances for an account should be inverted. */
export const invert_account = derived(
  [
    invert_income_liabilities_equity,
    name_income,
    name_liabilities,
    name_equity,
  ],
  ([
    $invert_income_liabilities_equity,
    $name_income,
    $name_liabilities,
    $name_equity,
  ]): ((name: string) => boolean) =>
    $invert_income_liabilities_equity
      ? (name) =>
          name.startsWith($name_income) ||
          name.startsWith($name_liabilities) ||
          name.startsWith($name_equity) ||
          name === _("Net Profit")
      : () => false,
);

/** Whether an account is closed before the given date. */
export const is_closed_account = derived(
  [account_details],
  ([$account_details]) =>
    (name: string, date: Date | null) => {
      const close_date = $account_details[name]?.close_date;
      if (!close_date) {
        return false;
      }
      return date == null ? true : close_date < date;
    },
);
