import { account_hierarchy_validator } from "../charts/hierarchy";
import {
  Document,
  entryBaseValidator,
  entryValidator,
  Event,
  Transaction,
} from "../entries";
import type { ValidationT } from "../lib/validation";
import {
  array,
  boolean,
  date,
  number,
  object,
  optional,
  record,
  string,
  tuple,
  unknown,
} from "../lib/validation";
import type { ImportableFile } from "../reports/import";
import { query_validator } from "../reports/query/query_table";

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
const error_validator = object<BeancountError>({
  type: string,
  message: string,
  source: optional(object({ filename: string, lineno: number })),
});

/** Validator for the details for a single account. */
const account_details = record(
  object({
    balance_string: optional(string),
    close_date: optional(date),
    last_entry: optional(object({ date, entry_hash: string })),
    uptodate_status: optional(string),
  }),
);

/** Validator for the Fava options that are used in the frontend. */
const fava_options = object({
  auto_reload: boolean,
  currency_column: number,
  conversion_currencies: array(string),
  collapse_pattern: array(string),
  import_config: optional(string),
  indent: number,
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

const importable_files_validator = array<ImportableFile>(
  object({
    name: string,
    basename: string,
    importers: array(
      object({
        account: string,
        importer_name: string,
        date: optional(string),
        name: optional(string),
      }),
    ),
  }),
);

const date_range = object({ begin: date, end: date });

const commodities = array(
  object({ base: string, quote: string, prices: array(tuple(date, number)) }),
);

export type Commodities = ValidationT<typeof commodities>;

const context = object({
  entry: entryBaseValidator,
  balances_before: optional(record(array(string))),
  balances_after: optional(record(array(string))),
  sha256sum: string,
  slice: string,
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
const source = object<SourceFile>({
  file_path: string,
  sha256sum: string,
  source: string,
});

const tree_report = object({
  charts: unknown,
  trees: array(account_hierarchy_validator),
  date_range: optional(date_range),
});

export const getAPIValidators = {
  balance_sheet: tree_report,
  account_report: object({
    charts: unknown,
    journal: optional(string),
    dates: optional(array(date_range)),
    interval_balances: optional(array(account_hierarchy_validator)),
    budgets: optional(record(array(account_budget))),
  }),
  changed: boolean,
  commodities,
  context,
  documents: array(Document.validator),
  errors: array(error_validator),
  events: array(Event.validator),
  extract: array(entryValidator),
  imports: importable_files_validator,
  income_statement: tree_report,
  ledger_data: ledgerDataValidator,
  move: string,
  payee_accounts: array(string),
  payee_transaction: Transaction.validator,
  query: query_validator,
  source,
  trial_balance: tree_report,
};

export type GetAPIValidators = typeof getAPIValidators;
