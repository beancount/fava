import type { EntryBaseAttributes } from "../entries";
import { entryBaseValidator, entryValidator, Transaction } from "../entries";
import type { Validator } from "../lib/validation";
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
import type { ImportableFile } from "../reports/import/load";
import { ledgerDataValidator } from "../stores";

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

/** A Beancount error that should be shown to the user in the list of errors. */
export interface BeancountError {
  message: string;
  source: { filename: string; lineno: number } | null;
  entry: EntryBaseAttributes | null;
}

const error_validator = object({
  message: string,
  source: optional(object({ filename: string, lineno: number })),
  entry: optional(entryBaseValidator),
}) satisfies Validator<BeancountError>;

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
