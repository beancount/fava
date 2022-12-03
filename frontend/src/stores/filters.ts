import { derived, writable } from "svelte/store";

/** The time filter. */
export const time_filter = writable("");
/** The account filter. */
export const account_filter = writable("");
/** The filter with our custom query syntax. */
export const fql_filter = writable("");

/** The three entry filters that Fava supports. */
// this screws up the API type definitions otherwise
// eslint-disable-next-line @typescript-eslint/consistent-type-definitions
export type Filters = {
  account: string;
  filter: string;
  time: string;
};

/** The current filters, can be used as URL parameters. */
export const filter_params = derived(
  [time_filter, account_filter, fql_filter],
  ([time, account, filter]): Filters => ({ time, account, filter })
);

export function getURLFilters(url: URL): Filters {
  return {
    account: url.searchParams.get("account") ?? "",
    filter: url.searchParams.get("filter") ?? "",
    time: url.searchParams.get("time") ?? "",
  };
}
