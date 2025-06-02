import { derived } from "svelte/store";

import { derived_array } from "../lib/store";
import { ledgerData } from ".";

/** Fava's options */
const fava_options = derived(ledgerData, (v) => v.fava_options);

/** The customized currency conversion select list */
export const conversion_currencies = derived_array(
  fava_options,
  ($fava_options) => $fava_options.conversion_currencies,
);
export const locale = derived(
  fava_options,
  ($fava_options) => $fava_options.locale,
);
export const collapse_pattern = derived_array(
  fava_options,
  ($fava_options) => $fava_options.collapse_pattern,
);
export const import_config = derived(
  fava_options,
  ($fava_options) => $fava_options.import_config,
);
export const invert_income_liabilities_equity = derived(
  fava_options,
  ($fava_options) => $fava_options.invert_income_liabilities_equity,
);
export const show_accounts_with_zero_balance = derived(
  fava_options,
  ($fava_options) => $fava_options.show_accounts_with_zero_balance,
);
export const show_accounts_with_zero_transactions = derived(
  fava_options,
  ($fava_options) => $fava_options.show_accounts_with_zero_transactions,
);
export const show_closed_accounts = derived(
  fava_options,
  ($fava_options) => $fava_options.show_closed_accounts,
);
export const uptodate_indicator_grey_lookback_days = derived(
  fava_options,
  ($fava_options) => $fava_options.uptodate_indicator_grey_lookback_days,
);
export const currency_column = derived(
  fava_options,
  ($fava_options) => $fava_options.currency_column,
);
export const indent = derived(
  fava_options,
  ($fava_options) => $fava_options.indent,
);
export const use_external_editor = derived(
  fava_options,
  ($fava_options) => $fava_options.use_external_editor,
);
export const auto_reload = derived(
  fava_options,
  ($fava_options) => $fava_options.auto_reload,
);
// TODO: equality comparison
export const insert_entry = derived(
  fava_options,
  ($fava_options) => $fava_options.insert_entry,
);
