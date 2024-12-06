import { log_error } from "../log";
import { set_mtime } from "../stores/mtime";
import {
  defaultValue,
  isJsonObject,
  object,
  string,
  unknown,
} from "./validation";

class FetchError extends Error {}

/** Wrapper around fetch with some default options */
export async function fetch(
  input: string,
  init: RequestInit = {},
): Promise<Response> {
  return window.fetch(input, { credentials: "same-origin", ...init });
}

/**
 * Handles JSON content for a Promise returned by fetch, also handling an HTTP
 * error status.
 */
async function handleJSON(
  response: Response,
): Promise<Record<string, unknown>> {
  const data: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    throw new FetchError(
      isJsonObject(data) && typeof data.error === "string"
        ? data.error
        : response.statusText,
    );
  }
  if (!isJsonObject(data)) {
    throw new FetchError("Invalid response: not a valid JSON object");
  }
  return data;
}

const response_validator = object({
  data: unknown,
  mtime: defaultValue(string, () => null),
});

export async function fetchJSON(
  input: string,
  init?: RequestInit,
): Promise<unknown> {
  const res = await fetch(input, init).then(handleJSON);
  const validated = response_validator(res).unwrap_or(null);
  if (validated) {
    if (typeof validated.mtime === "string") {
      set_mtime(validated.mtime);
    }
    return validated.data;
  }
  log_error(res);
  throw new FetchError("Invalid response: missing data or mtime key.");
}

/**
 * Handles text content for a Promise returned by fetch, also handling an HTTP
 * error status.
 */
export async function handleText(response: Response): Promise<string> {
  if (!response.ok) {
    const msg = await response.text().catch(() => response.statusText);
    throw new FetchError(msg);
  }
  return response.text();
}
