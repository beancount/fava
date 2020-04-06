import { object, record, string, unknown } from "./lib/validation";
import { favaAPI } from "./stores";

/**
 * Select a single element.
 */
export function select(
  expr: string,
  con: Document | Element = document
): Element | null {
  return con.querySelector(expr);
}

export function getScriptTagJSON(selector: string): unknown {
  const el = select(selector);
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

/**
 * Execute the callback of the event of given type is fired on something
 * matching selector.
 */
export function delegate<T extends Event, C extends HTMLElement>(
  element: Element | Document | null,
  type: string,
  selector: string,
  callback: (e: T, c: C) => void
): void {
  if (!element) {
    return;
  }
  element.addEventListener(type, (event) => {
    let { target } = event;
    if (!target || !(target instanceof Node)) {
      return;
    }
    if (!(target instanceof Element)) {
      target = target.parentNode;
    }
    if (target instanceof HTMLElement) {
      const closest = target.closest(selector);
      if (closest) {
        callback(event as T, closest as C);
      }
    }
  });
}

/**
 * Bind an event to element, only run the callback once.
 */
export function once(
  element: EventTarget,
  event: string,
  callback: (ev: Event) => void
): void {
  function runOnce(ev: Event): void {
    element.removeEventListener(event, runOnce);
    callback.apply(element, [ev]);
  }

  element.addEventListener(event, runOnce);
}

/**
 * Handles JSON content for a Promise returned by fetch, also handling an HTTP
 * error status.
 */
export async function handleJSON(response: Response): Promise<unknown> {
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  const data = await response.json();
  if (!data.success) {
    throw new Error(data.error);
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

const validateAPIResponse = object({ data: unknown });

/**
 * Get the URL string for one of Fava's reports.
 */
export function urlFor(
  report: string,
  params?: Record<string, string>
): string {
  const url = `${favaAPI.baseURL}${report}`;
  if (!params) {
    return url;
  }
  const urlParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    urlParams.set(key, value);
  });
  return `${url}?${urlParams.toString()}`;
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
  const url = urlFor(`api/${endpoint}`, params);
  const responseData = await fetch(url);
  const json = await handleJSON(responseData);
  return validateAPIResponse(json).data;
}

const putAPIValidators = {
  add_entries: string,
  format_source: string,
  source: string,
};

type apiTypes = typeof putAPIValidators;

/**
 * Fetch an API endpoint and convert the JSON data to an object.
 * @param endpoint - the endpoint to fetch
 * @param params - a string to append as params or an object.
 */
export async function putAPI<T extends keyof apiTypes>(
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
