import { get as store_get } from "svelte/store";

import type { Entry } from "../entries";
import { urlForRaw } from "../helpers";
import { fetchJSON } from "../lib/fetch";
import type { ValidationT } from "../lib/validation";
import { string } from "../lib/validation";
import { notify, notify_err } from "../notifications";
import router from "../router";
import type { Filters, FiltersConversionInterval } from "../stores/filters";
import type { GetAPIValidators, SourceFile } from "./validators";
import { getAPIValidators } from "./validators";

class InvalidResponseDataError extends Error {
  constructor(cause: Error) {
    super("Invalid data returned in API request.", { cause });
    notify_err(this);
  }
}

/** Required arguments for the various PUT API endpoints. */
interface PutAPIInputs {
  add_document: FormData;
  upload_import_file: FormData;
  add_entries: { entries: Entry[] };
  attach_document: { filename: string; entry_hash: string };
  format_source: { source: string };
  source: SourceFile;
  source_slice: { entry_hash: string; source: string; sha256sum: string };
}

/**
 * PUT to an API endpoint and convert the returned JSON data to an object.
 * @param endpoint - the endpoint to fetch
 * @param body - either a FormData instance or an object that will be converted
 *               to JSON.
 * @returns the response message string
 */
export async function put<T extends keyof PutAPIInputs>(
  endpoint: T,
  body: PutAPIInputs[T],
): Promise<string> {
  const opts =
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
}

interface GetAPIParams {
  balance_sheet: FiltersConversionInterval;
  account_report: FiltersConversionInterval & { a: string; r: string };
  changed: undefined;
  commodities: Filters;
  context: { entry_hash: string };
  documents: Filters;
  errors: undefined;
  events: Filters;
  extract: { filename: string; importer: string };
  imports: undefined;
  income_statement: FiltersConversionInterval;
  trial_balance: FiltersConversionInterval;
  ledger_data: undefined;
  move: { filename: string; account: string; new_name: string };
  options: undefined;
  payee_accounts: { payee: string };
  payee_transaction: { payee: string };
  query: Filters & { query_string: string };
  source: { filename: string };
}

/**
 * Fetch an API endpoint and convert the JSON data to an object.
 * @param endpoint - the endpoint to fetch
 * @param params - a string to append as params or an object.
 * @returns the validated response returned by the endpoint.
 */
export async function get<T extends keyof GetAPIParams>(
  endpoint: T,
  ...[params]: GetAPIParams[T] extends undefined
    ? [undefined?, number?]
    : [GetAPIParams[T], number?]
): Promise<ValidationT<GetAPIValidators[T]>> {
  const $urlForRaw = store_get(urlForRaw);
  const url = $urlForRaw(`api/${endpoint}`, params);
  const json = await fetchJSON(url);
  const res = getAPIValidators[endpoint](json);
  if (res.is_ok) {
    return res.value as ValidationT<GetAPIValidators[T]>;
  }
  throw new InvalidResponseDataError(res.error);
}

interface DeleteAPIParams {
  document: { filename: string };
  source_slice: { entry_hash: string; sha256sum: string };
}

/**
 * Delete an API endpoint and convert the JSON data to an object.
 * @param endpoint - the endpoint to fetch
 * @param params - a string to append as params or an object.
 * @returns the response returned by the endpoint.
 */
export async function doDelete<T extends keyof DeleteAPIParams>(
  endpoint: T,
  params: DeleteAPIParams[T],
): Promise<string> {
  const $urlForRaw = store_get(urlForRaw);
  const url = $urlForRaw(`api/${endpoint}`, params);
  const json = await fetchJSON(url, { method: "DELETE" });
  const res = string(json);
  if (res.is_ok) {
    return res.value;
  }
  throw new InvalidResponseDataError(res.error);
}

/**
 * Move a file, either in an import directory or a document.
 * @param filename - the current name of the file.
 * @param account - account to move the file to.
 * @param new_name - the new filename.
 * @returns whether the file was moved successfully.
 */
export async function moveDocument(
  filename: string,
  account: string,
  new_name: string,
): Promise<boolean> {
  try {
    const msg = await get("move", { filename, account, new_name });
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
export async function deleteDocument(filename: string): Promise<boolean> {
  try {
    const msg = await doDelete("document", { filename });
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
export async function saveEntries(entries: Entry[]): Promise<void> {
  if (!entries.length) {
    return;
  }
  try {
    const data = await put("add_entries", { entries });
    router.reload();
    notify(data);
  } catch (error) {
    notify_err(error, (e) => `Saving failed: ${e.message}`);
    throw error;
  }
}
