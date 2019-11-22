import { writable } from "svelte/store";

const stored_history_string = localStorage.getItem("fava-query-history");
let initialList = [];
if (stored_history_string) {
  initialList = JSON.parse(stored_history_string);
}
export const query_shell_history = writable(initialList);
query_shell_history.subscribe(val => {
  if (val.length) {
    localStorage.setItem("fava-query-history", JSON.stringify(val));
  }
});

export function addToHistory(query: string): void {
  if (query) {
    query_shell_history.update(hist => {
      hist.unshift(query);
      return [...new Set(hist)];
    });
  }
}
