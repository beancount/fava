import type { Readable } from "svelte/store";
import { derived, get as store_get, writable } from "svelte/store";

import { _ } from "../i18n";
import { isDescendant, parent } from "../lib/account";
import { derived_array } from "../lib/store";
import { account_details, accounts_internal, fava_options, options } from ".";

// a derived_array to avoid recreating collapsed_accounts too often.
const collapse_patterns = derived_array(
  fava_options,
  ($fava_options) => $fava_options.collapse_pattern,
);

/** The accounts that are toggled via the collapse-pattern option. */
const collapsed_accounts: Readable<readonly string[]> = derived(
  [collapse_patterns, accounts_internal],
  ([$collapse_patterns, $accounts_internal]) => {
    const matchers = $collapse_patterns.map((pattern) => new RegExp(pattern));
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
        $accounts_internal
          .filter((a) => a !== account && isDescendant(a, account))
          .forEach((child) => {
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
      .filter((a) => isDescendant(a, account))
      .forEach((descendant) => {
        new_explicitly_toggled.set(descendant, false);
      });
    return new_explicitly_toggled;
  });
}

/** Whether the balances for an account should be inverted. */
export const invert_account = derived(
  [fava_options, options],
  ([$fava_options, $options]): ((name: string) => boolean) =>
    $fava_options.invert_income_liabilities_equity
      ? (name) =>
          name.startsWith($options.name_income) ||
          name.startsWith($options.name_liabilities) ||
          name.startsWith($options.name_equity) ||
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
      return date === null ? true : close_date < date;
    },
);
