import { derived } from "svelte/store";

import { derived_array } from "../lib/store";
import { ledgerData } from ".";

/** Beancount's options */
const options = derived(ledgerData, (v) => v.options);
/** Beancount ledger title */
export const ledger_title = derived(options, ($options) => $options.title);
/** The operating currencies (sorted). */
export const operating_currency = derived_array(options, ($options) =>
  [...$options.operating_currency].sort(),
);
const filename = derived(options, ($options) => $options.filename);
const include = derived_array(options, ($options) => $options.include);
/** All included files, with the main one first. */
export const sources = derived(
  [filename, include],
  ([$filename, $include]) => new Set([$filename, ...$include]),
);

export const documents = derived_array(
  options,
  ($options) => $options.documents,
);
export const name_assets = derived(options, ($options) => $options.name_assets);
export const name_equity = derived(options, ($options) => $options.name_equity);
export const name_expenses = derived(
  options,
  ($options) => $options.name_expenses,
);
export const name_income = derived(options, ($options) => $options.name_income);
export const name_liabilities = derived(
  options,
  ($options) => $options.name_liabilities,
);
