import { isJsonObject, string } from "./validation";

/** Wrapper around fetch with some default options */
export function fetch(
  input: string,
  init: RequestInit = {}
): Promise<Response> {
  return window.fetch(input, {
    credentials: "same-origin",
    ...init,
  });
}

/**
 * Handles JSON content for a Promise returned by fetch, also handling an HTTP
 * error status.
 */
export async function handleJSON(response: Response): Promise<unknown> {
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  const data: unknown = await response.json();
  if (!isJsonObject(data)) {
    throw new Error("Invalid response");
  }
  if (!data.success) {
    throw new Error(string(data.error));
  }
  return data;
}

/**
 * Handles text content for a Promise returned by fetch, also handling an HTTP
 * error status.
 */
export async function handleText(response: Response): Promise<string> {
  if (!response.ok) {
    const msg = await response.text();
    throw new Error(msg || response.statusText);
  }
  return response.text();
}
