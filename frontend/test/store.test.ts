import { deepEqual, equal, throws } from "node:assert/strict";
import { beforeEach, test } from "node:test";

import { get as store_get, writable } from "svelte/store";

import { derived_array, localStorageSyncedStore } from "../src/lib/store.ts";
import { string } from "../src/lib/validation.ts";
import { setup_jsdom } from "./dom.ts";

beforeEach(setup_jsdom);

test("derived store", () => {
  const source = writable<string[]>([]);
  const derived = derived_array(source, (s) => s);
  let source_count = 0;
  source.subscribe(() => {
    source_count += 1;
  });
  let derived_count = 0;
  derived.subscribe(() => {
    derived_count += 1;
  });
  source.set([]);
  source.set([]);
  source.set(["a", "b"]);
  source.set(["a", "b"]);
  source.set(["a", "b"]);
  equal(source_count, 6);
  equal(derived_count, 2);
});

test("localStorage-synced stores", () => {
  const a = localStorageSyncedStore("test-store", string, () => "default");
  equal(a.key, "fava-test-store");
  deepEqual(a.values(), []);

  // Getting the value will temporarily attach a subscriber (and unsubscribe as well).
  localStorage.removeItem(a.key);
  equal(store_get(a), "default");

  localStorage.setItem(a.key, "invalid-non-json-stringified");
  equal(store_get(a), "default");

  localStorage.setItem(a.key, JSON.stringify("value"));
  equal(store_get(a), "value");

  a.set("another-value");
  equal(store_get(a), "another-value");
  equal(localStorage.getItem(a.key), JSON.stringify("another-value"));

  a.update(() => "a-value");
  equal(store_get(a), "a-value");
  equal(localStorage.getItem(a.key), JSON.stringify("a-value"));

  const seen_values: string[] = [];
  const unsubscribe = a.subscribe((v) => {
    seen_values.push(v);
  });
  window.dispatchEvent(
    new StorageEvent("storage", {
      key: a.key,
      newValue: JSON.stringify("event-value-different-storage-area"),
      storageArea: sessionStorage,
    }),
  );
  window.dispatchEvent(
    new StorageEvent("storage", {
      key: "fava-wrong-key",
      newValue: JSON.stringify("event-value-wrong-key"),
      storageArea: localStorage,
    }),
  );
  window.dispatchEvent(
    new StorageEvent("storage", {
      key: a.key,
      newValue: JSON.stringify("event-value"),
      storageArea: localStorage,
    }),
  );
  unsubscribe();
  deepEqual(seen_values, ["a-value", "event-value"]);

  throws(() => {
    // The prefix is added automatically.
    localStorageSyncedStore("fava-test-store", string, () => "value");
  });
  throws(() => {
    // No duplicate stores
    localStorageSyncedStore("test-store", string, () => "value");
  });
});
