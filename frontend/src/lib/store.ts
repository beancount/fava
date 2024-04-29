import type { Readable, Writable } from "svelte/store";
import { derived, writable } from "svelte/store";

import type { StrictEquality } from "./equals";
import { shallow_equal } from "./equals";
import { parseJSON } from "./json";
import type { Validator } from "./validation";

/**
 * Create a derived store that does a shallow array equality check.
 * @param store - The store to derive the value from.
 * @param getter - A getter that obtains the array that should be contained in the store.
 */
export function derived_array<S, T extends StrictEquality>(
  store: Readable<S>,
  getter: (values: S) => readonly T[],
): Readable<readonly T[]> {
  let val: readonly T[] = [];
  return derived(
    store,
    (store_val, set) => {
      const newVal = getter(store_val);
      if (!shallow_equal(val, newVal)) {
        set(newVal);
        val = newVal;
      }
    },
    val,
  );
}

/** A store that has its value synced to localStorage. */
export type LocalStoreSyncedStore<T> = Writable<T> & {
  /** List all the values that this store can take. */
  values: () => [T, string][];
};

/**
 * Create a store that syncs its value to localStorage.
 * @param key - The key to save this with in localStorage.
 * @param validator - A Validator to check the loaded value.
 * @param init - A default to initialise the store with if localStorage is empty.
 * @param values - An optional enumerator of all possible values and descriptions.
 */
export function localStorageSyncedStore<T>(
  key: string,
  validator: Validator<T>,
  init: () => T,
  values: () => [T, string][] = () => [],
): LocalStoreSyncedStore<T> {
  const fullKey = `fava-${key}`;

  // Create a store which is empty first but reads the value from
  // localStorage on the first subscription.
  const store = writable<T>(undefined, (set) => {
    const stored_val = localStorage.getItem(fullKey);
    let initial: T | null = null;
    if (stored_val != null) {
      const val = parseJSON(stored_val).and_then(validator).unwrap_or(null);
      if (val !== null) {
        initial = val;
      }
    }
    set(initial ?? init());

    store.subscribe((val) => {
      localStorage.setItem(fullKey, JSON.stringify(val));
    });
  });

  return { ...store, values };
}
