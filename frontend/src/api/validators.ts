import { entryBaseValidator, entryValidator, Transaction } from "../entries";
import type { ValidationT, Validator } from "../lib/validation";
import {
  array,
  boolean,
  constant,
  date,
  number,
  object,
  optional,
  record,
  string,
  tuple,
  union,
  unknown,
} from "../lib/validation";
import type { ImportableFile } from "../reports/import/load";

/** A Beancount error that should be shown to the user in the list of errors. */
export interface BeancountError {
  message: string;
  source: { filename: string; lineno: number } | null;
}

const error_validator = object({
  message: string,
  source: optional(object({ filename: string, lineno: number })),
}) satisfies Validator<BeancountError>;

export const ledgerDataValidator = object({
  accounts: array(string),
  account_details: record(
    object({
      close_date: date,
      uptodate_status: optional(string),
      last_entry: optional(object({ date, entry_hash: string })),
      balance_string: optional(string),
    })
  ),
  base_url: string,
  currencies: array(string),
  errors: array(error_validator),
  fava_options: object({
    auto_reload: boolean,
    currency_column: number,
    conversion_currencies: array(string),
    import_config: optional(string),
    indent: number,
    locale: union(string, constant(null)),
    uptodate_indicator_grey_lookback_days: number,
    insert_entry: array(
      object({ date: string, filename: string, lineno: number, re: string })
    ),
    use_external_editor: boolean,
  }),
  have_excel: boolean,
  incognito: boolean,
  links: array(string),
  options: object({
    documents: array(string),
    filename: string,
    include: array(string),
    operating_currency: array(string),
    title: string,
  }),
  payees: array(string),
  precisions: record(number),
  tags: array(string),
  years: array(string),
  user_queries: array(object({ name: string, query_string: string })),
  upcoming_events_count: number,
  extension_reports: array(tuple([string, string])),
  sidebar_links: array(tuple([string, string])),
  other_ledgers: array(tuple([string, string])),
});

export type LedgerData = ValidationT<typeof ledgerDataValidator>;

const importable_files_validator: Validator<ImportableFile[]> = array(
  object({
    name: string,
    basename: string,
    importers: array(
      object({
        account: string,
        importer_name: string,
        date: optional(string),
        name: optional(string),
      })
    ),
  })
);

export const getAPIValidators = {
  changed: boolean,
  context: object({
    entry: entryBaseValidator,
    balances_before: optional(record(array(string))),
    balances_after: optional(record(array(string))),
    sha256sum: string,
    slice: string,
  }),
  commodities: array(
    object({
      base: string,
      quote: string,
      prices: array(tuple([date, number])),
    })
  ),
  documents: array(object({ account: string, filename: string, date: string })),
  errors: array(error_validator),
  extract: array(entryValidator),
  events: array(object({ type: string, description: string, date })),
  imports: importable_files_validator,
  move: string,
  payee_accounts: array(string),
  payee_transaction: Transaction.validator,
  query_result: object({ chart: unknown, table: string }),
  source: object({ source: string, sha256sum: string, file_path: string }),
  ledger_data: ledgerDataValidator,
};

export type GetAPITypes = typeof getAPIValidators;
