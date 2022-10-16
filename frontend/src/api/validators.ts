import { entryBaseValidator, entryValidator, Transaction } from "../entries";
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
import { importable_files_validator } from "../reports/import/helpers";
import { ledgerDataValidator } from "../stores";

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
  errors: number,
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
