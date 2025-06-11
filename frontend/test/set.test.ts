import { test } from "uvu";
import * as assert from "uvu/assert";

import { toggle } from "../src/lib/set";

test("toggle set elements", () => {
  assert.equal(toggle(new Set([0, 1]), 0), new Set([1]));
  assert.equal(toggle(new Set(["0", 1]), 0), new Set(["0", 0, 1]));
  assert.equal(toggle(new Set([0, 1]), 2), new Set([0, 1, 2]));
});

test.run();
