import { deepEqual, equal, ok } from "node:assert/strict";
import { test } from "node:test";

import { is_non_empty, move } from "../src/lib/array.ts";

test("check array is non-empty", () => {
  equal(is_non_empty([]), false);
  ok(is_non_empty([1]));
});

test("move array elements", () => {
  const initital = [0, 1, 2, 3];
  const moved = move(initital, 1, 2);
  deepEqual(moved, [0, 2, 1, 3]);
  deepEqual(initital, [0, 1, 2, 3]);
});
