import { equal, ok } from "node:assert/strict";
import { test } from "node:test";

import { is_empty } from "../src/lib/objects.ts";

test("check whether objects are empty", () => {
  ok(is_empty({}));
  equal(is_empty({ asdf: "asdf" }), false);
});
