import { derived, Readable, Writable, writable } from "svelte/store";

import { shallow_equal } from "./equals";
import { Validator } from "./validation";

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
  const stored_val = localStorage.getItem(key);
  const initial = stored_val ? validator(JSON.parse(stored_val)) : init();

  const store = writable(initial);

  store.subscribe((val) => {
    localStorage.setItem(key, JSON.stringify(val));
  });
  return store;
}
