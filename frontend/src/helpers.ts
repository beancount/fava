import { fetch, handleJSON } from "./lib/fetch";
import { object, record, string, unknown } from "./lib/validation";
import { baseURL, urlSyncedParams } from "./stores/url";

export function getScriptTagJSON(selector: string): unknown {
  const el = document.querySelector(selector);
  return el ? JSON.parse(el.innerHTML) : null;
}

let translations: Record<string, string>;

/**
 * Translate the given string.
 */
export function _(text: string): string {
  if (translations === undefined) {
    translations = record(string)(getScriptTagJSON("#translations"));
  }
  return translations[text] || text;
}

const validateAPIResponse = object({ data: unknown });

let baseURL_val = "";
baseURL.subscribe((val) => {
  baseURL_val = val;
});

/**
 * Get the URL string for one of Fava's reports.
 */
export function urlFor(
  report: string,
  params?: Record<string, string>,
  update = true
): string {
  const url = `${baseURL_val}${report}`;
  const urlParams = new URLSearchParams();
  if (update) {
    const oldParams = new URL(window.location.href).searchParams;
    for (const name of urlSyncedParams) {
      const value = oldParams.get(name);
      if (value) {
        urlParams.set(name, value);
      }
    }
  }
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      urlParams.set(key, value);
    });
  }
  const urlParamString = urlParams.toString();
  return urlParamString ? `${url}?${urlParams.toString()}` : url;
}

/** Url for the account page for an account. */
export function accountUrl(account: string): string {
  return new URL(urlFor(`account/${account}`), window.location.href).toString();
}

/**
 * Fetch an API endpoint and convert the JSON data to an object.
 * @param endpoint - the endpoint to fetch
 * @param params - a string to append as params or an object.
 */
export async function fetchAPI(
  endpoint: string,
  params?: Record<string, string>
): Promise<unknown> {
  const url = urlFor(`api/${endpoint}`, params, false);
  const responseData = await fetch(url);
  const json = await handleJSON(responseData);
  return validateAPIResponse(json).data;
}
