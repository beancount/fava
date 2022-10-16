import type { Entry } from "../entries";
import { urlFor } from "../helpers";
import { fetchJSON } from "../lib/fetch";
import type { ValidationT } from "../lib/validation";
import { string } from "../lib/validation";
import { notify, notify_err } from "../notifications";
import router from "../router";
import type { Filters } from "../stores/filters";

import type { GetAPITypes } from "./validators";
import { getAPIValidators } from "./validators";

/** Required arguments for the various PUT API endpoints. */
interface PutAPIInputs {
  add_document: FormData;
  add_entries: { entries: Entry[] };
  attach_document: { filename: string; entry_hash: string };
  format_source: { source: string };
  source: { file_path: string; source: string; sha256sum: string };
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
  body: PutAPIInputs[T]
): Promise<string> {
  const opts =
    body instanceof FormData
      ? { body }
      : {
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        };
  const url = urlFor(`api/${endpoint}`);
  const json = await fetchJSON(url, { method: "PUT", ...opts });
  const res = string(json);
  if (res.success) {
    return res.value;
  }
  notify(`Invalid data returned in API request: ${res.value}`, "error");
  throw new Error(res.value);
}

interface GetAPIParams {
  changed: undefined;
  commodities: Filters;
  context: { entry_hash: string };
  errors: undefined;
  extract: { filename: string; importer: string };
  events: Filters;
  documents: Filters;
  ledger_data: undefined;
  imports: undefined;
  source: { filename: string };
  move: { filename: string; account: string; new_name: string };
  payee_accounts: { payee: string };
  payee_transaction: { payee: string };
  query_result: Filters & { query_string: string };
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
): Promise<ValidationT<GetAPITypes[T]>> {
  const url = urlFor(`api/${endpoint}`, params, false);
  const json = await fetchJSON(url);
  const res = getAPIValidators[endpoint](json);
  if (res.success) {
    return res.value as ValidationT<GetAPITypes[T]>;
  }
  notify(`Invalid data returned in API request: ${res.value}`, "error");
  throw new Error(res.value);
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
  new_name: string
): Promise<boolean> {
  try {
    const msg = await get("move", { filename, account, new_name });
    notify(msg);
    return true;
  } catch (error) {
    notify_err(error, (e) => e.message);
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
    const url = urlFor("api/document", { filename }, false);
    const res = await fetchJSON(url, { method: "DELETE" });
    const d = string(res);
    notify(d.value);
    return d.success;
  } catch (error) {
    notify_err(error, (e) => e.message);
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
