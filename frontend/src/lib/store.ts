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
  /** The key that this is stored under in localStorage. */
  key: string;
  /** List all the values that this store can take. */
  values: () => [T, string][];
};

/** Keep track of all created stores. */
const local_storage_synced_stores = new Set();

/**
 * Create a store that syncs its value to localStorage.
 * @param key - The key to save this with in localStorage (will be prefixed with `fava-`).
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
  if (key.startsWith("fava")) {
    throw new Error("INTERNAL: should be called without 'fava-' prefix.");
  }
  const full_key = `fava-${key}`;
  if (local_storage_synced_stores.has(full_key)) {
    throw new Error(`INTERNAL: duplicate store with key '${key}'.`);
  }
  local_storage_synced_stores.add(full_key);

  // Create a store which is empty first but reads the value from
  // localStorage on the first subscription.
  const {
    set: store_set,
    update: store_update,
    subscribe,
  } = writable<T>(undefined, (set) => {
    const set_from_stored_value = (stored: string | null) => {
      let initial: T | null = null;
      if (stored != null) {
        const res = parseJSON(stored).and_then(validator);
        if (res.is_ok) {
          initial = res.value;
        }
      }
      set(initial ?? init());
    };
    set_from_stored_value(localStorage.getItem(full_key));

    const listener = (event: StorageEvent) => {
      if (event.storageArea === localStorage && event.key === full_key) {
        set_from_stored_value(event.newValue);
      }
    };

    window.addEventListener("storage", listener);
    return () => {
      window.removeEventListener("storage", listener);
    };
  });

  return {
    set: (val: T) => {
      localStorage.setItem(full_key, JSON.stringify(val));
      store_set(val);
    },
    update: (updater) => {
      store_update((old_val) => {
        const val = updater(old_val);
        localStorage.setItem(full_key, JSON.stringify(val));
        return val;
      });
    },
    subscribe,
    key: full_key,
    values,
  };
}
