import { derived, writable } from "svelte/store";

export const urlSyncedParams = [
  "account",
  "charts",
  "conversion",
  "filter",
  "interval",
  "time",
];

/** The current URL pathname. Should only be updated by the router. */
export const pathname = writable<string>();

/** The current URL search. Should only be updated by the router. */
export const search = writable<string>();

/** The current URL searchParams. */
export const searchParams = derived(search, (s) => new URLSearchParams(s));

/** The query string containing all values that are synced to the URL. */
export const synced_query_string = derived([search], ([s]) => {
  const all_params = new URLSearchParams(s);
  const params = new URLSearchParams();
  for (const name of urlSyncedParams) {
    const value = all_params.get(name);
    if (value) {
      params.set(name, value);
    } else {
      params.delete(name);
    }
  }
  const str = params.toString();
  return str ? `?${str}` : str;
});
