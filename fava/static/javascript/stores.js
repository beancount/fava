import { writable } from "svelte/store";

export const urlHash = writable("");

export function closeOverlay() {
  if (window.location.hash) {
    window.location.hash = "";
  }
  urlHash.set("");
}

export const conversion = writable("");
export const interval = writable("");
export const showCharts = writable(true);
export const activeChart = writable({});
export const chartMode = writable("treemap");
export const chartCurrency = writable("");
