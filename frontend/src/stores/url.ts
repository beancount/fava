import type { Readable } from "svelte/store";
import { derived, writable } from "svelte/store";

/** The current URL hash. */
export const urlHash = writable("");

/** The current URL pathname. Should only be updated by the router. */
export const pathname = writable<string>();

/** The current URL search. Should only be updated by the router. */
export const search = writable<string>();

/** The current URL searchParams. */
export const searchParams: Readable<URLSearchParams> = derived(
  search,
  ($search) => new URLSearchParams($search),
);

/** These URL parameters for filters and conversion / interval are synced for most links. */
const synced_search_param_names = [
  "account",
  "charts",
  "conversion",
  "filter",
  "interval",
  "time",
];

/** The current searchParamscontaining all values that are synced to the URL. */
export const syncedSearchParams: Readable<URLSearchParams> = derived(
  searchParams,
  ($searchParams) => {
    const params = new URLSearchParams();
    for (const name of synced_search_param_names) {
      const value = $searchParams.get(name);
      if (value != null && value) {
        params.set(name, value);
      }
    }
    return params;
  },
);

export function closeOverlay(): void {
  if (window.location.hash) {
    window.history.pushState(null, "", "#");
  }
  urlHash.set("");
}
