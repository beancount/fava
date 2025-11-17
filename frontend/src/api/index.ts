import { get as store_get } from "svelte/store";

import {
  Document,
  type Entry,
  entryValidator,
  Event,
  Transaction,
} from "../entries/index.ts";
import type { NonEmptyArray } from "../lib/array.ts";
import { fetch_json } from "../lib/fetch.ts";
import type { Validator } from "../lib/validation.ts";
import { array, boolean, number, object, string } from "../lib/validation.ts";
import { notify, notify_err } from "../notifications.ts";
import { query_validator } from "../reports/query/query_table.ts";
import { router } from "../router.ts";
import { base_url } from "../stores/index.ts";
import { set_mtime } from "../stores/mtime.ts";
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
  | "journal_page"
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

type ApiParams = Partial<{
  a: string;
  account: string;
  conversion: string;
  entry_hash: string;
  filename: string;
  filter: string;
  importer: string;
  interval: string;
  narration: string;
  order: "asc" | "desc";
  page: number;
  payee: string;
  query_string: string;
  r: string;
  sha256sum: string;
  time: string;
}>;
type ApiParam = keyof ApiParams;

function api_url(endpoint: ApiEndpoint): URL;
function api_url(
  endpoint: ApiEndpoint,
  accepted_params: readonly ApiParam[],
  params: Partial<ApiParams>,
): URL;
function api_url(
  endpoint: ApiEndpoint,
  accepted_params?: readonly ApiParam[],
  params?: Partial<ApiParams>,
): URL {
  const $base_url = store_get(base_url);
  const url = new URL(`${$base_url}api/${endpoint}`, window.location.href);
  if (accepted_params && params) {
    for (const key of accepted_params) {
      const value = params[key];
      if (value != null && value !== "") {
        url.searchParams.set(key, value.toString());
      }
    }
  }
  return url;
}

async function fetch_and_handle_api_call<R>(
  url: URL,
  init: RequestInit,
  validator: Validator<R>,
): Promise<R> {
  const json = await fetch_json(url, init);
  if (typeof json.mtime === "string") {
    set_mtime(json.mtime);
  }
  const res = validator(json.data);
  return res.unwrap(InvalidResponseDataError);
}

/**
 * Define a function to call the endpoint with the required parameters.
 */
function define_endpoint<T extends readonly ApiParam[], R>(
  endpoint: ApiEndpoint,
  validator: Validator<R>,
  accepted_params: T,
  method: "DELETE" | "GET" | "PUT" = "GET",
): (params: Pick<ApiParams, T[number]>) => Promise<R> {
  return async (params) => {
    const url = api_url(endpoint, accepted_params, params);
    return fetch_and_handle_api_call(url, { method }, validator);
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
    const url = api_url(endpoint);
    return fetch_and_handle_api_call(url, { method: "GET" }, validator);
  };
}

/**
 * Define a function to call the PUT endpoint with FormData.
 */
function define_put_form(
  endpoint: PutEndpoint,
): (body: FormData) => Promise<string> {
  return async (body) => {
    const url = api_url(endpoint);
    return fetch_and_handle_api_call(url, { method: "PUT", body }, string);
  };
}

/**
 * Define a function to call the PUT endpoint with a JSON body.
 */
function define_put_json(
  endpoint: PutEndpoint,
): (body: unknown) => Promise<string> {
  return async (body) => {
    const url = api_url(endpoint);
    return fetch_and_handle_api_call(
      url,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      },
      string,
    );
  };
}

// DELETE endpoints

const delete_document_raw = define_endpoint(
  "document",
  string,
  ["filename"],
  "DELETE",
);
export const delete_source_slice = define_endpoint(
  "source_slice",
  string,
  ["entry_hash", "sha256sum"],
  "DELETE",
);

const filters = ["account", "filter", "time"] as const;
const filters_conversion_interval = [
  "account",
  "conversion",
  "filter",
  "interval",
  "time",
] as const;

// GET endpoints

export const get_account_report = define_endpoint(
  "account_report",
  account_report_validator,
  [...filters_conversion_interval, "a", "r"],
);
export const get_balance_sheet = define_endpoint(
  "balance_sheet",
  tree_report_validator,
  filters_conversion_interval,
);
export const get_changed = define_paramless_endpoint("changed", boolean);
export const get_commodities = define_endpoint(
  "commodities",
  commodities_validator,
  filters,
);
export const get_context = define_endpoint("context", context_validator, [
  "entry_hash",
]);
export const get_documents = define_endpoint(
  "documents",
  array(Document.validator),
  filters,
);
export const get_errors = define_paramless_endpoint(
  "errors",
  array(error_validator),
);
export const get_events = define_endpoint(
  "events",
  array(Event.validator),
  filters,
);
export const get_extract = define_endpoint("extract", array(entryValidator), [
  "filename",
  "importer",
]);
export const get_imports = define_paramless_endpoint(
  "imports",
  importable_files_validator,
);
export const get_income_statement = define_endpoint(
  "income_statement",
  tree_report_validator,
  filters_conversion_interval,
);
export const get_journal_page = define_endpoint(
  "journal_page",
  object({ journal: string, total_pages: number }),
  [...filters_conversion_interval, "page", "order"],
);
export const get_ledger_data = define_paramless_endpoint(
  "ledger_data",
  ledgerDataValidator,
);
export const get_narration_transaction = define_endpoint(
  "narration_transaction",
  Transaction.validator,
  ["narration"],
);
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
  ["payee"],
);
export const get_payee_transaction = define_endpoint(
  "payee_transaction",
  Transaction.validator,
  ["payee"],
);
export const get_query = define_endpoint("query", query_validator, [
  ...filters,
  "query_string",
]);
export const get_source = define_endpoint("source", source_validator, [
  "filename",
]);
export const get_source_slice = define_endpoint(
  "source_slice",
  object({ slice: string, sha256sum: string }),
  ["entry_hash"],
);
export const get_statistics = define_endpoint(
  "statistics",
  statistics_validator,
  filters,
);
export const get_trial_balance = define_endpoint(
  "trial_balance",
  tree_report_validator,
  filters_conversion_interval,
);

type Put<T> = (body: T) => Promise<string>;

// PUT endpoints

export const put_add_document = define_put_form("add_document");
const put_add_entries: Put<{ entries: NonEmptyArray<Entry> }> =
  define_put_json("add_entries");
export const put_attach_document: Put<{
  filename: string;
  entry_hash: string;
}> = define_put_json("attach_document");
export const put_format_source: Put<{ source: string }> =
  define_put_json("format_source");
const put_move: Put<{
  filename: string;
  account: string;
  new_name: string;
}> = define_put_json("move");
export const put_source: Put<SourceFile> = define_put_json("source");
export const put_source_slice: Put<{
  entry_hash: string;
  source: string;
  sha256sum: string;
}> = define_put_json("source_slice");
export const put_upload_import_file = define_put_form("upload_import_file");

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
