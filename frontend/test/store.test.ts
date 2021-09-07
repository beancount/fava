import { writable } from "svelte/store";
import { test } from "uvu";
import assert from "uvu/assert";

import { derived_array } from "../src/lib/store";

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

test.run();
