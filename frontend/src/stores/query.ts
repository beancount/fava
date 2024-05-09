import { localStorageSyncedStore } from "../lib/store";
import { array, string } from "../lib/validation";

const { update, set, subscribe } = localStorageSyncedStore(
  "query-history",
  array(string),
  () => [],
);

/** The query shell history. */
export const query_shell_history = {
  subscribe,
  /** Completely clear the history. */
  clear(): void {
    set([]);
  },
  /** Add a new entry to the query history (this does avoid duplicates). */
  add(query: string): void {
    if (query) {
      update((hist) => [...new Set([query, ...hist])]);
    }
  },
  /** Remove a query string from the query history. */
  remove(query: string): void {
    if (query) {
      update((hist) => hist.filter((item) => item !== query));
    }
  },
};
