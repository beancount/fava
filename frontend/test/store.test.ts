import { get as store_get, writable } from "svelte/store";
import { test } from "uvu";
import * as assert from "uvu/assert";

import { derived_array, localStorageSyncedStore } from "../src/lib/store";
import { string } from "../src/lib/validation";
import { setup_jsdom } from "./dom";

test.before.each(setup_jsdom);

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
  assert.is(source_count, 6);
  assert.is(derived_count, 2);
});

test("localStorage-synced stores", () => {
  const a = localStorageSyncedStore("test-store", string, () => "default");
  assert.equal(a.key, "fava-test-store");
  assert.equal(a.values(), []);

  // Getting the value will temporarily attach a subscriber (and unsubscribe as well).
  localStorage.removeItem(a.key);
  assert.equal(store_get(a), "default");

  localStorage.setItem(a.key, "invalid-non-json-stringified");
  assert.equal(store_get(a), "default");

  localStorage.setItem(a.key, JSON.stringify("value"));
  assert.equal(store_get(a), "value");

  a.set("another-value");
  assert.equal(store_get(a), "another-value");
  assert.equal(localStorage.getItem(a.key), JSON.stringify("another-value"));

  a.update(() => "a-value");
  assert.equal(store_get(a), "a-value");
  assert.equal(localStorage.getItem(a.key), JSON.stringify("a-value"));

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
  assert.equal(seen_values, ["a-value", "event-value"]);

  assert.throws(() => {
    // The prefix is added automatically.
    localStorageSyncedStore("fava-test-store", string, () => "value");
  });
  assert.throws(() => {
    // No duplicate stores
    localStorageSyncedStore("test-store", string, () => "value");
  });
});

test.run();
