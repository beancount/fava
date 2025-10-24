import { test } from "uvu";
import * as assert from "uvu/assert";

import { shallow_equal } from "../src/lib/equals.ts";

test("shallow array equality", () => {
  assert.ok(shallow_equal([], []));
  assert.ok(shallow_equal(["asdf", 1], ["asdf", 1]));
  assert.ok(!shallow_equal([1, "asdf"], ["asdf", 1]));
  assert.ok(shallow_equal(["asdf"], ["asdf"]));
});

test.run();
