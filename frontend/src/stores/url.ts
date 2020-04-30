import { writable } from "svelte/store";

/** The Fava base URL for the current Beancount file. */
export const baseURL = writable("");

export const urlSyncedParams = [
  "account",
  "charts",
  "conversion",
  "filter",
  "interval",
  "time",
];
