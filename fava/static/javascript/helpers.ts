import { object, record, string, unknown } from "./validation";
import { favaAPI } from "./stores";

/**
 * Select a single element.
 */
export function select(expr: string, con: Document | Element = document) {
  return con.querySelector(expr);
}

/**
 * Select multiple elements (and convert NodeList to Array).
 */
export function selectAll(expr: string, con: Document | Element = document) {
  return Array.from(con.querySelectorAll(expr));
}

export function getScriptTagJSON(selector: string): unknown {
  const el = select(selector);
  if (!el) {
    return null;
  }
  return JSON.parse(el.innerHTML);
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
export function delegate<T extends Event, C extends Element>(
  element: Element | Document | null,
  type: string,
  selector: string,
  callback: (e: T, c: C) => void
) {
  if (!element) {
    return;
  }
  element.addEventListener(type, event => {
    let { target } = event;
    if (!target || !(target instanceof Node)) {
      return;
    }
    if (!(target instanceof Element)) {
      target = target.parentNode;
    }
    if (target instanceof Element) {
      const closest = (target as HTMLElement).closest(selector);
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
) {
  function runOnce(ev: Event) {
    element.removeEventListener(event, runOnce);
    callback.apply(element, [ev]);
  }

  element.addEventListener(event, runOnce);
}

export function ready() {
  return new Promise(resolve => {
    if (document.readyState !== "loading") {
      resolve();
    } else {
      document.addEventListener("DOMContentLoaded", resolve);
    }
  });
}

/**
 * Handles JSON content for a Promise returned by fetch, also handling an HTTP
 * error status.
 */
export function handleJSON(response: Response): Promise<unknown> {
  if (!response.ok) {
    return Promise.reject(response.statusText);
  }
  return response.json().then(data => {
    if (!data.success) {
      return Promise.reject(data.error);
    }
    return data;
  });
}

/**
 * Handles text content for a Promise returned by fetch, also handling an HTTP
 * error status.
 */
export function handleText(response: Response): Promise<string> {
  if (!response.ok) {
    return Promise.reject(response.statusText);
  }
  return response.text();
}

export function fetch(input: string, init = {}) {
  const defaults: RequestInit = {
    credentials: "same-origin",
  };
  return window.fetch(input, Object.assign(defaults, init));
}

const validateAPIResponse = object({ data: unknown });

/**
 * Get the URL string for one of Fava's reports.
 */
export function urlFor(
  report: string,
  params?: Record<string, string>
): string {
  let url = `${favaAPI.baseURL}${report}`;
  if (params) {
    const urlParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      urlParams.set(key, value);
    });
    url += `?${urlParams.toString()}`;
  }
  return url;
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
  const json: unknown = await handleJSON(responseData);
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
  body: any
): Promise<ReturnType<apiTypes[T]>> {
  const res = await fetch(`${favaAPI.baseURL}api/${endpoint}/`, {
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
 * Fuzzy match a pattern against a string.
 *
 * Returns true if all characters of `pattern` can be found in order in
 * `string`. For lowercase characters in `pattern` match both lower and upper
 * case, for uppercase only an exact match counts.
 */
export function fuzzytest(pattern: string, text: string) {
  let pindex = 0;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const search = pattern[pindex];
    if (char === search || char.toLowerCase() === search) {
      pindex += 1;
    }
  }
  return pindex === pattern.length;
}

/**
 * Wrap fuzzy matched characters.
 *
 * Wrap all occurences of characters of `pattern` (in order) in `string` in
 * <span> tags.
 */
export function fuzzywrap(pattern: string, text: string) {
  let pindex = 0;
  const result = [];
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const search = pattern[pindex];
    if (char === search || char.toLowerCase() === search) {
      result.push(`<span>${char}</span>`);
      pindex += 1;
    } else {
      result.push(char);
    }
  }
  return result.join("");
}
