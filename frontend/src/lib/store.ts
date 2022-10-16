import type { Readable, Writable } from "svelte/store";
import { derived, writable } from "svelte/store";

import { shallow_equal } from "./equals";
import { parseJSON } from "./json";
import type { Validator } from "./validation";

/**
 * Create a derived store that does a shallow array equality check.
 * @param store - The store to derive the value from.
 * @param getter - A getter that obtains the array that should be contained in the store.
 */
export function derived_array<S, T>(
  store: Readable<S>,
  getter: (values: S) => T[]
): Readable<T[]> {
  let val: T[] = [];
  return derived(
    store,
    (store_val, set) => {
      const newVal = getter(store_val);
      if (!shallow_equal(val, newVal)) {
        set(newVal);
        val = newVal;
      }
    },
    val
  );
}

/**
 * Create a store that syncs its value to localStorage.
 * @param key - The key to save this with in localStorage.
 * @param validator - A Validator to check the loaded value.
 * @param init - A default to initialise the store with if localStorage is
 *               empty.
 */
export function localStorageSyncedStore<T>(
  key: string,
  validator: Validator<T>,
  init: () => T
): Writable<T> {
  const fullKey = `fava-${key}`;

  // Create a store which is empty first but reads the value from
  // localStorage on the first subscription.
  const store = writable<T>(undefined, (set) => {
    const stored_val = localStorage.getItem(fullKey);
    let initial: T | null = null;
    if (stored_val) {
      const json = parseJSON(stored_val);
      const parsed = json.success ? validator(json.value) : null;
      if (parsed?.success) {
        initial = parsed.value;
      }
    }
    set(initial ?? init());

    store.subscribe((val) => {
      localStorage.setItem(fullKey, JSON.stringify(val));
    });
  });

  return store;
}
