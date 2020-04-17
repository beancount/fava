import { Readable, derived } from "svelte/store";
import { shallow_equal } from "./equals";

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
