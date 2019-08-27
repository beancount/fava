import { writable } from "svelte/store";

export const urlHash = writable("");

export const conversion = writable("");
export const interval = writable("");
export const showCharts = writable(true);

export const activeChart = writable({});
export const chartMode = writable("treemap");
export const chartCurrency = writable("");

export const favaAPI = {};

export const filters = writable({
  time: "",
  filter: "",
  account: "",
});

export const urlSyncedParams = [
  "account",
  "charts",
  "conversion",
  "filter",
  "interval",
  "time",
];

export function closeOverlay() {
  if (window.location.hash) {
    window.history.pushState({}, "", "#");
  }
  urlHash.set("");
}
