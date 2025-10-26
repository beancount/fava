import { deepEqual } from "node:assert/strict";
import { test } from "node:test";

import { toggle } from "../src/lib/set.ts";

test("toggle set elements", () => {
  deepEqual(toggle(new Set([0, 1]), 0), new Set([1]));
  deepEqual(toggle(new Set(["0", 1]), 0), new Set(["0", 0, 1]));
  deepEqual(toggle(new Set([0, 1]), 2), new Set([0, 1, 2]));
});
