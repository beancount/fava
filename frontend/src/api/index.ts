import { get as store_get } from "svelte/store";

import {
  Document,
  type Entry,
  entryValidator,
  Event,
  Transaction,
} from "../entries/index.ts";
import { urlForRaw } from "../helpers.ts";
import type { NonEmptyArray } from "../lib/array.ts";
import { fetchJSON } from "../lib/fetch.ts";
import type { Validator } from "../lib/validation.ts";
import { array, boolean, string } from "../lib/validation.ts";
import { notify, notify_err } from "../notifications.ts";
import { query_validator } from "../reports/query/query_table.ts";
import { router } from "../router.ts";
import type { Filters, FiltersConversionInterval } from "../stores/filters.ts";
import {
  account_report_validator,
  commodities_validator,
  context_validator,
  error_validator,
  importable_files_validator,
  ledgerDataValidator,
  options_validator,
  source_validator,
  type SourceFile,
  statistics_validator,
  tree_report_validator,
} from "./validators.ts";

class InvalidResponseDataError extends Error {
  constructor(cause: Error) {
    super("Invalid data returned in API request.", { cause });
    notify_err(this);
  }
}

// This module contains wrapper functions (get_*, delete_*, put_* functions
// below) to call the API endpoints defined in json_api.py.
//
// For each HTTP endpoint, a function with types for the parameters and
// a validator for the response should be added to this module.
type DeleteEndpoint = "document" | "source_slice";
type GetEndpoint =
  | "balance_sheet"
  | "account_report"
  | "changed"
  | "commodities"
  | "context"
  | "documents"
  | "errors"
  | "events"
  | "extract"
  | "imports"
  | "income_statement"
  | "trial_balance"
  | "ledger_data"
  | "options"
  | "payee_accounts"
  | "payee_transaction"
  | "narration_transaction"
  | "narrations"
  | "query"
  | "source"
  | "statistics";
type PutEndpoint =
  | "add_document"
  | "add_entries"
  | "attach_document"
  | "format_source"
  | "move"
  | "source"
  | "source_slice"
  | "upload_import_file";

type ApiEndpoint = DeleteEndpoint | GetEndpoint | PutEndpoint;

/**
 * Define a function to call the endpoint with the required parameters.
 */
// eslint-disable-next-line @typescript-eslint/no-unnecessary-type-parameters
function define_endpoint<T extends Record<string, string>, R>(
  endpoint: ApiEndpoint,
  validator: Validator<R>,
  method: "DELETE" | "GET" | "PUT" = "GET",
): (params: T) => Promise<R> {
  return async (params) => {
    const $urlForRaw = store_get(urlForRaw);
    const url = $urlForRaw(`api/${endpoint}`, params);
    const json = await fetchJSON(url, { method });
    const res = validator(json);
    if (res.is_ok) {
      return res.value;
    }
    throw new InvalidResponseDataError(res.error);
  };
}

/**
 * Define a function to call an endpoint without parameters.
 */
function define_paramless_endpoint<R>(
  endpoint: ApiEndpoint,
  validator: Validator<R>,
): () => Promise<R> {
  return async () => {
    const $urlForRaw = store_get(urlForRaw);
    const url = $urlForRaw(`api/${endpoint}`);
    const json = await fetchJSON(url, { method: "GET" });
    const res = validator(json);
    if (res.is_ok) {
      return res.value;
    }
    throw new InvalidResponseDataError(res.error);
  };
}

/**
 * Define a function to call the PUT endpoint with the required typed parameters.
 */
// eslint-disable-next-line @typescript-eslint/no-unnecessary-type-parameters
function define_put<T>(endpoint: PutEndpoint): (body: T) => Promise<string> {
  return async (body) => {
    const opts: RequestInit =
      body instanceof FormData
        ? { body }
        : {
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
          };
    const $urlForRaw = store_get(urlForRaw);
    const url = $urlForRaw(`api/${endpoint}`);
    const json = await fetchJSON(url, { method: "PUT", ...opts });
    const res = string(json);
    if (res.is_ok) {
      return res.value;
    }
    throw new InvalidResponseDataError(res.error);
  };
}

// With the use of satisfies and this helper type we can achieve partial type inference
// on the endpoint definitions below.
type Api<T> = (params: T) => unknown;

// DELETE endpoints

const delete_document_raw = define_endpoint(
  "document",
  string,
  "DELETE",
) satisfies Api<{
  filename: string;
}>;
export const delete_source_slice = define_endpoint(
  "source_slice",
  string,
  "DELETE",
) satisfies Api<{
  entry_hash: string;
  sha256sum: string;
}>;

// GET endpoints

export const get_account_report = define_endpoint(
  "account_report",
  account_report_validator,
) satisfies Api<FiltersConversionInterval & { a: string; r: string }>;
export const get_balance_sheet = define_endpoint(
  "balance_sheet",
  tree_report_validator,
) satisfies Api<FiltersConversionInterval>;
export const get_changed = define_paramless_endpoint("changed", boolean);
export const get_commodities = define_endpoint(
  "commodities",
  commodities_validator,
) satisfies Api<Filters>;
export const get_context = define_endpoint(
  "context",
  context_validator,
) satisfies Api<{
  entry_hash: string;
}>;
export const get_documents = define_endpoint(
  "documents",
  array(Document.validator),
) satisfies Api<Filters>;
export const get_errors = define_paramless_endpoint(
  "errors",
  array(error_validator),
);
export const get_events = define_endpoint(
  "events",
  array(Event.validator),
) satisfies Api<Filters>;
export const get_extract = define_endpoint(
  "extract",
  array(entryValidator),
) satisfies Api<{ filename: string; importer: string }>;
export const get_imports = define_paramless_endpoint(
  "imports",
  importable_files_validator,
);
export const get_income_statement = define_endpoint(
  "income_statement",
  tree_report_validator,
) satisfies Api<FiltersConversionInterval>;
export const get_ledger_data = define_paramless_endpoint(
  "ledger_data",
  ledgerDataValidator,
);
export const get_narration_transaction = define_endpoint(
  "narration_transaction",
  Transaction.validator,
) satisfies Api<{ narration: string }>;
export const get_narrations = define_paramless_endpoint(
  "narrations",
  array(string),
);
export const get_options = define_paramless_endpoint(
  "options",
  options_validator,
);
export const get_payee_accounts = define_endpoint(
  "payee_accounts",
  array(string),
) satisfies Api<{ payee: string }>;
export const get_payee_transaction = define_endpoint(
  "payee_transaction",
  Transaction.validator,
) satisfies Api<{ payee: string }>;
export const get_query = define_endpoint(
  "query",
  query_validator,
) satisfies Api<Filters & { query_string: string }>;
export const get_source = define_endpoint(
  "source",
  source_validator,
) satisfies Api<{ filename: string }>;
export const get_statistics = define_endpoint(
  "statistics",
  statistics_validator,
) satisfies Api<Filters>;
export const get_trial_balance = define_endpoint(
  "trial_balance",
  tree_report_validator,
) satisfies Api<FiltersConversionInterval>;

// PUT endpoints

export const put_add_document = define_put<FormData>("add_document");
const put_add_entries = define_put<{ entries: NonEmptyArray<Entry> }>(
  "add_entries",
);
export const put_attach_document = define_put<{
  filename: string;
  entry_hash: string;
}>("attach_document");
export const put_format_source = define_put<{ source: string }>(
  "format_source",
);
const put_move = define_put<{
  filename: string;
  account: string;
  new_name: string;
}>("move");
export const put_source = define_put<SourceFile>("source");
export const put_source_slice = define_put<{
  entry_hash: string;
  source: string;
  sha256sum: string;
}>("source_slice");
export const put_upload_import_file =
  define_put<FormData>("upload_import_file");

/**
 * Move a file, either in an import directory or a document.
 * @param filename - the current name of the file.
 * @param account - account to move the file to.
 * @param new_name - the new filename.
 * @returns whether the file was moved successfully.
 */
export async function move_document(
  filename: string,
  account: string,
  new_name: string,
): Promise<boolean> {
  try {
    const msg = await put_move({ filename, account, new_name });
    notify(msg);
    return true;
  } catch (error) {
    notify_err(error);
    return false;
  }
}

/**
 * Delete a file, either in an import directory or a document.
 * @param filename - the filename of the file to delete.
 * @returns whether the file was deleted successfully.
 */
export async function delete_document(filename: string): Promise<boolean> {
  try {
    const msg = await delete_document_raw({ filename });
    notify(msg);
    return true;
  } catch (error) {
    notify_err(error);
    return false;
  }
}

/**
 * Save an array of entries.
 * @param entries - an array of entries to save to the Beancount file.
 */
export async function save_entries(
  entries: NonEmptyArray<Entry>,
): Promise<void> {
  try {
    const msg = await put_add_entries({ entries });
    router.reload();
    notify(msg);
  } catch (error) {
    notify_err(error, (e) => `Saving failed: ${e.message}`);
    throw error;
  }
}
