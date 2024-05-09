import type { Readable } from "svelte/store";
import { derived, writable } from "svelte/store";

export const urlHash = writable("");

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
export const searchParams: Readable<Readonly<URLSearchParams>> = derived(
  search,
  ($search) => new URLSearchParams($search),
);

/** The query string containing all values that are synced to the URL. */
export const synced_query_string = derived([searchParams], ([s]) => {
  const params = new URLSearchParams();
  for (const name of urlSyncedParams) {
    const value = s.get(name);
    if (value != null && value) {
      params.set(name, value);
    } else {
      params.delete(name);
    }
  }
  const str = params.toString();
  return str ? `?${str}` : str;
});

export function closeOverlay(): void {
  if (window.location.hash) {
    window.history.pushState(null, "", "#");
  }
  urlHash.set("");
}
