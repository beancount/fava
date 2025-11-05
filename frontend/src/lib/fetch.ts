import { isJsonObject, object, string } from "./validation.ts";

export class FetchError extends Error {}

export class FetchHTTPError extends FetchError {
  readonly status: number;

  constructor(message: string | null, status: number) {
    super(
      message != null
        ? `HTTP ${status.toString()} - ${message}`
        : `HTTP ${status.toString()}`,
    );
    this.status = status;
  }
}

export class FetchInvalidResponseError extends FetchError {
  constructor(msg: string) {
    super(`Invalid response: ${msg}`);
  }
}

const error_response_validator = object({ error: string });

/**
 * Fetch JSON content, also handling an HTTP error status.
 *
 * Checks for an object at the top JSON level. For errors, looks
 * for an error message like `{ "error": "error message" }
 */
export async function fetch_json(
  input: URL,
  init?: RequestInit,
): Promise<Record<string, unknown>> {
  const response = await fetch(input, init);
  const json: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    throw new FetchHTTPError(
      error_response_validator(json)
        .map((d) => d.error)
        .unwrap_or(null),
      response.status,
    );
  }
  if (!isJsonObject(json)) {
    throw new FetchInvalidResponseError("Not a valid JSON object");
  }
  return json;
}

/**
 * Fetch text content, also handling an HTTP error status.
 */
export async function fetch_text(
  input: string | URL,
  init?: RequestInit,
): Promise<string> {
  const response = await fetch(input, init);
  if (!response.ok) {
    const message = await response.text().catch(() => null);
    throw new FetchHTTPError(message, response.status);
  }
  return response.text();
}
