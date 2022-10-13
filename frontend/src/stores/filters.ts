import { derived, writable } from "svelte/store";

/** The time filter. */
export const time_filter = writable("");
/** The account filter. */
export const account_filter = writable("");
/** The filter with our custom query syntax. */
export const fql_filter = writable("");

/** The three entry filters that Fava supports. */
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
