import { derived, writable } from "svelte/store";

import { getInterval } from "../lib/interval.ts";

/** The current URL. Should only be updated by the router. */
export const current_url = writable<URL>();

/** The current URL hash. */
export const hash = derived(current_url, (u) => u.hash.slice(1));

/** The current URL pathname. */
export const pathname = derived(current_url, (u) => u.pathname);

/** The current URL search. */
const search = derived(current_url, (u) => u.search);

/** The current URL searchParams. */
export const searchParams = derived(
  search,
  ($search) => new URLSearchParams($search),
);

/** Whether the charts should be shown. */
export const show_charts = derived(
  searchParams,
  ($searchParams) => $searchParams.get("charts") !== "false",
);

/** The current conversion used for reports. */
export const conversion = derived(
  searchParams,
  ($searchParams) => $searchParams.get("conversion") ?? "at_cost",
);

/** The current interval used for reports. */
export const interval = derived(searchParams, ($searchParams) =>
  getInterval($searchParams.get("interval")),
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

/** The current searchParams containing all values that are synced to the URL. */
export const syncedSearchParams = derived(searchParams, ($searchParams) => {
  const params = new URLSearchParams();
  for (const name of synced_search_param_names) {
    const value = $searchParams.get(name);
    if (value != null && value) {
      params.set(name, value);
    }
  }
  return params;
});
