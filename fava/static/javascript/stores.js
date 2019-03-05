import { writable } from "svelte/store";

export const urlHash = writable("");

export function closeOverlay() {
  if (window.location.hash) {
    window.location.hash = "";
  }
  urlHash.set("");
}
