import { derived } from "svelte/store";

import { _ } from "../i18n";
import { account_details, fava_options, options } from ".";

/** Whether an account should be collapsed in the account trees. */
export const collapse_account = derived(fava_options, ($fava_options) => {
  const matchers = $fava_options.collapse_pattern.map((p) => new RegExp(p));
  return (name: string) => matchers.some((p) => p.test(name));
});

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
