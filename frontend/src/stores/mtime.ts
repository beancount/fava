import { derived, writable } from "svelte/store";

const ledger_mtime_writable = writable(BigInt("0"));

/**
 * Last file change to one of the source files of the current ledger.
 */
export const ledger_mtime = derived(ledger_mtime_writable, (v) => v);

/**
 * Set the mtime from the given string value.
 */
export function set_mtime(text: string): void {
  const new_value = BigInt(text);
  ledger_mtime_writable.update((v) => (new_value > v ? new_value : v));
}

/**
 * Read the mtime from the HTML source.
 */
export function read_mtime(): void {
  const el = document.getElementById("ledger-mtime");
  const text = el?.textContent;
  if (text) {
    el.remove();
    set_mtime(text);
  }
}
