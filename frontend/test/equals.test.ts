import { ok } from "node:assert/strict";
import { test } from "node:test";

import { shallow_equal } from "../src/lib/equals.ts";

test("shallow array equality", () => {
  ok(shallow_equal([], []));
  ok(shallow_equal(["asdf", 1], ["asdf", 1]));
  ok(!shallow_equal([1, "asdf"], ["asdf", 1]));
  ok(shallow_equal(["asdf"], ["asdf"]));
});
