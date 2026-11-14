import type { Readable } from "svelte/store";
import { get as store_get, writable } from "svelte/store";

const ledger_mtime_writable = writable(BigInt("0"));

/**
 * Last file change to one of the source files of the current ledger.
 */
export const ledger_mtime: Readable<bigint> = ledger_mtime_writable;

/** The oldest mtime in the responses received for the load with a signal. */
const load_mtimes = new WeakMap<AbortSignal, bigint>();

/**
 * Whether all data received for the load with this signal is for the current mtime.
 */
export function has_current_mtime(signal: AbortSignal): boolean {
  return load_mtimes.get(signal) === store_get(ledger_mtime);
}

/**
 * Set the mtime from the given string value.
 *
 * If it is from a response for a load with an abort signal, also track it for that.
 */
export function set_mtime(text: string, signal?: AbortSignal | null): void {
  const new_value = text.startsWith("X")
    ? // the timestamp is replaced by a sequence of `X` in incognito mode.
      BigInt(text.replaceAll("X", "1"))
    : BigInt(text);
  if (signal) {
    const oldest = load_mtimes.get(signal);
    if (oldest == null || new_value < oldest) {
      load_mtimes.set(signal, new_value);
    }
  }
  // biome-ignore lint/complexity/useMathMinMax: Math.max does not work for BigInt
  ledger_mtime_writable.update((v) => (new_value > v ? new_value : v));
}

/**
 * Read the mtime from the HTML source.
 */
export function read_mtime(signal?: AbortSignal): void {
  const el = document.getElementById("ledger-mtime");
  const text = el?.textContent;
  if (text != null) {
    el?.remove();
    set_mtime(text, signal);
  }
}
