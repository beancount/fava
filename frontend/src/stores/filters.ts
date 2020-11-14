import { get, writable } from "svelte/store";

export const time_filter = writable("");
export const account_filter = writable("");
export const fql_filter = writable("");

interface Filters {
  account: string;
  filter: string;
  time: string;
}

export function getFilterParams(): Filters {
  return {
    account: get(account_filter),
    filter: get(fql_filter),
    time: get(time_filter),
  };
}
