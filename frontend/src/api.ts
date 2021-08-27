import type { Entry } from "./entries";
import { entryValidator, Transaction } from "./entries";
import { urlFor } from "./helpers";
import { fetch, handleJSON } from "./lib/fetch";
import {
  array,
  boolean,
  number,
  object,
  string,
  unknown,
} from "./lib/validation";
import { log_error } from "./log";
import { notify } from "./notifications";
import router from "./router";

const validateAPIResponse = object({ data: unknown });
/** Return types for the various PUT API endpoints. */
const putAPIValidators = {
  add_document: string,
  add_entries: string,
  attach_document: string,
  format_source: string,
  source: string,
  source_slice: string,
};
type PutAPITypes = typeof putAPIValidators;
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
 */
export async function put<T extends keyof PutAPITypes>(
  endpoint: T,
  body: PutAPIInputs[T]
): Promise<ReturnType<PutAPITypes[T]>> {
  const opts =
    body instanceof FormData
      ? { body }
      : {
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        };
  const url = urlFor(`api/${endpoint}`);
  const res = await fetch(url, { method: "PUT", ...opts }).then(handleJSON);
  const { data } = validateAPIResponse(res);
  return putAPIValidators[endpoint](data) as ReturnType<PutAPITypes[T]>;
}

const getAPIValidators = {
  changed: boolean,
  context: object({
    content: string,
    sha256sum: string,
    slice: string,
  }),
  errors: number,
  extract: array(entryValidator),
  payee_accounts: array(string),
  move: string,
  payee_transaction: Transaction.validator,
  query_result: object({
    chart: unknown,
    table: string,
  }),
};
type GetAPITypes = typeof getAPIValidators;

/**
 * Fetch an API endpoint and convert the JSON data to an object.
 * @param endpoint - the endpoint to fetch
 * @param params - a string to append as params or an object.
 */
export async function get<T extends keyof GetAPITypes>(
  endpoint: T,
  params?: Record<string, string>
): Promise<ReturnType<GetAPITypes[T]>> {
  const url = urlFor(`api/${endpoint}`, params, false);
  const responseData = await fetch(url);
  const json = await handleJSON(responseData);
  const { data }: { data: unknown } = validateAPIResponse(json);
  return getAPIValidators[endpoint](data) as ReturnType<GetAPITypes[T]>;
}

/**
 * Move a file, either in an import directory or a document.
 * @returns whether the file was moved successfully.
 */
export async function moveDocument(
  filename: string,
  account: string,
  newName: string
): Promise<boolean> {
  try {
    const msg = await get("move", {
      filename,
      account,
      newName,
    });
    notify(string(msg));
    return true;
  } catch (error) {
    if (error instanceof Error) {
      notify(error.message, "error");
    }
    return false;
  }
}

/**
 * Delete a file, either in an import directory or a document.
 * @returns whether the file was deleted successfully.
 */
export async function deleteDocument(filename: string): Promise<boolean> {
  try {
    const url = urlFor("api/document", { filename }, false);
    const res = await fetch(url, { method: "DELETE" }).then(handleJSON);
    const { data }: { data: unknown } = validateAPIResponse(res);
    notify(string(data));
    return true;
  } catch (error) {
    if (error instanceof Error) {
      notify(error.message, "error");
    }
    return false;
  }
}

/**
 * Save an array of entries.
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
    log_error(error);
    if (error instanceof Error) {
      notify(`Saving failed: ${error.message}`, "error");
    }
    throw error;
  }
}
