import { fetchAPI, handleJSON, urlFor } from "./helpers";
import { notify } from "./notifications";
import { string, object, unknown } from "./lib/validation";

const validateAPIResponse = object({ data: unknown });
const putAPIValidators = {
  add_entries: string,
  format_source: string,
  source: string,
  source_slice: string,
};

type apiTypes = typeof putAPIValidators;

/**
 * Fetch an API endpoint and convert the JSON data to an object.
 * @param endpoint - the endpoint to fetch
 * @param params - a string to append as params or an object.
 */
export async function put<T extends keyof apiTypes>(
  endpoint: T,
  body: unknown
): Promise<ReturnType<apiTypes[T]>> {
  const res = await fetch(urlFor(`api/${endpoint}`), {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  }).then(handleJSON);
  const { data }: { data: unknown } = validateAPIResponse(res);
  return putAPIValidators[endpoint](data) as ReturnType<apiTypes[T]>;
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
    const msg = await fetchAPI("move", {
      filename,
      account,
      newName,
    });
    notify(string(msg));
    return true;
  } catch (error) {
    notify(error, "error");
    return false;
  }
}
