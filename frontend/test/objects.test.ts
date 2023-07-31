import { test } from "uvu";
import assert from "uvu/assert";

import { is_empty } from "../src/lib/objects";

test("check whether objects are empty", () => {
  assert.ok(is_empty({}));
  assert.not(is_empty({ asdf: "asdf" }));
});

test.run();
