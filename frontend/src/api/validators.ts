import { account_hierarchy_validator } from "../charts/hierarchy.ts";
import { chart_validator } from "../charts/index.ts";
import { entryBaseValidator } from "../entries/index.ts";
import type { ValidationT } from "../lib/validation.ts";
import {
  array,
  boolean,
  constants,
  date,
  number,
  object,
  optional,
  record,
  string,
  tuple,
} from "../lib/validation.ts";
import { Inventory } from "../reports/query/query_table.ts";

/** A Beancount error that should be shown to the user in the list of errors. */
export interface BeancountError {
  readonly type: string;
  readonly message: string;
  readonly source: {
    readonly filename: string;
    readonly lineno: number;
  } | null;
}

/** Validator for a BeancountError. */
export const error_validator = object<BeancountError>({
  type: string,
  message: string,
  source: optional(object({ filename: string, lineno: number })),
});

/** Validator for the details for a single account. */
const account_detail = object({
  balance_string: optional(string),
  close_date: optional(date),
  last_entry: optional(object({ date, entry_hash: string })),
  uptodate_status: optional(constants("green", "yellow", "red")),
});
const account_details = record(account_detail);

export type AccountDetail = ValidationT<typeof account_detail>;

/** Validator for the Fava options that are used in the frontend. */
const fava_options = object({
  auto_reload: boolean,
  currency_column: number,
  conversion_currencies: array(string),
  collapse_pattern: array(string),
  import_config: optional(string),
  indent: number,
  invert_gains_losses_colors: boolean,
  invert_income_liabilities_equity: boolean,
  show_closed_accounts: boolean,
  show_accounts_with_zero_balance: boolean,
  show_accounts_with_zero_transactions: boolean,
  locale: optional(string),
  uptodate_indicator_grey_lookback_days: number,
  insert_entry: array(
    object({ date: string, filename: string, lineno: number, re: string }),
  ),
  use_external_editor: boolean,
});

/** Validator for the Beancount options that are used in the frontend. */
const options = object({
  documents: array(string),
  filename: string,
  include: array(string),
  name_assets: string,
  name_equity: string,
  name_expenses: string,
  name_income: string,
  name_liabilities: string,
  operating_currency: array(string),
  title: string,
});

const extensions = array(
  object({
    name: string,
    report_title: optional(string),
    has_js_module: boolean,
  }),
);

export const ledgerDataValidator = object({
  account_details,
  accounts: array(string),
  base_url: string,
  currencies: array(string),
  currency_names: record(string),
  errors: array(error_validator),
  extensions,
  fava_options,
  have_excel: boolean,
  incognito: boolean,
  links: array(string),
  options,
  other_ledgers: array(tuple(string, string)),
  payees: array(string),
  precisions: record(number),
  sidebar_links: array(tuple(string, string)),
  tags: array(string),
  upcoming_events_count: number,
  user_queries: array(object({ name: string, query_string: string })),
  years: array(string),
});

export type LedgerData = ValidationT<typeof ledgerDataValidator>;

export const importable_files_validator = array(
  object({
    name: string,
    basename: string,
    importers: array(
      object({
        account: string,
        importer_name: string,
        date: string,
        name: string,
      }),
    ),
  }),
);

const date_range = object({ begin: date, end: date });

export const commodities_validator = array(
  object({ base: string, quote: string, prices: array(tuple(date, number)) }),
);

export type Commodities = ValidationT<typeof commodities_validator>;

export const context_validator = object({
  entry: entryBaseValidator,
  balances_before: optional(record(array(string))),
  balances_after: optional(record(array(string))),
});

const account_budget = object({
  budget: record(number),
  budget_children: record(number),
});
export type AccountBudget = ValidationT<typeof account_budget>;

/** One of the Beancount source files. */
export interface SourceFile {
  readonly file_path: string;
  readonly sha256sum: string;
  readonly source: string;
}
export const source_validator = object<SourceFile>({
  file_path: string,
  sha256sum: string,
  source: string,
});

export const tree_report_validator = object({
  charts: chart_validator,
  trees: array(account_hierarchy_validator),
  date_range: optional(date_range),
});

export const account_report_validator = object({
  charts: chart_validator,
  journal: optional(string),
  dates: optional(array(date_range)),
  interval_balances: optional(array(account_hierarchy_validator)),
  budgets: optional(record(array(account_budget))),
});

export const statistics_validator = object({
  all_balance_directives: string,
  entries_by_type: record(number),
  balances: record(Inventory.validator),
});

export const options_validator = object({
  fava_options: record(string),
  beancount_options: record(string),
});
