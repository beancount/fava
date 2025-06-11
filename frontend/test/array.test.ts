import { test } from "uvu";
import * as assert from "uvu/assert";

import { is_non_empty, move } from "../src/lib/array";

test("check array is non-empty", () => {
  assert.not(is_non_empty([]));
  assert.ok(is_non_empty([1]));
});

test("move array elements", () => {
  const initital = [0, 1, 2, 3];
  const moved = move(initital, 1, 2);
  assert.equal(moved, [0, 2, 1, 3]);
  assert.equal(initital, [0, 1, 2, 3]);
});

test.run();
