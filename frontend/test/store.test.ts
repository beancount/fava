import test from "ava";
import { writable } from "svelte/store";

import { derived_array } from "../src/lib/store";

test("derived store", (t) => {
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
  t.is(source_count, 6);
  t.is(derived_count, 2);
});
