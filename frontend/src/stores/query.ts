import { localStorageSyncedStore } from "../lib/store";
import { array, string } from "../lib/validation";

export const query_shell_history = localStorageSyncedStore(
  "query-history",
  array(string),
  () => []
);

export function addToHistory(query: string): void {
  if (query) {
    query_shell_history.update((hist) => {
      hist.unshift(query);
      return [...new Set(hist)];
    });
  }
}
