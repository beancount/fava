import { derived } from "svelte/store";

import { searchParams } from "./url.ts";

/** The time filter. */
export const time_filter = derived(
  searchParams,
  ($searchParams) => $searchParams.get("time") ?? "",
);
/** The account filter. */
export const account_filter = derived(
  searchParams,
  ($searchParams) => $searchParams.get("account") ?? "",
);
/** The filter with our custom query syntax. */
export const fql_filter = derived(
  searchParams,
  ($searchParams) => $searchParams.get("filter") ?? "",
);

/** The three entry filters that Fava supports. */
export interface Filters extends Record<string, string> {
  account: string;
  filter: string;
  time: string;
}

/** The three filters as well as conversion and interval. */
export interface FiltersConversionInterval extends Filters {
  conversion: string;
  interval: string;
}

/** The current filters, can be used as URL parameters. */
export const filter_params = derived(
  [time_filter, account_filter, fql_filter],
  ([$time_filter, $account_filter, $fql_filter]): Filters => ({
    time: $time_filter,
    account: $account_filter,
    filter: $fql_filter,
  }),
);

export function getURLFilters(url: URL): FiltersConversionInterval {
  return {
    account: url.searchParams.get("account") ?? "",
    filter: url.searchParams.get("filter") ?? "",
    time: url.searchParams.get("time") ?? "",
    conversion: url.searchParams.get("conversion") ?? "",
    interval: url.searchParams.get("interval") ?? "",
  };
}
