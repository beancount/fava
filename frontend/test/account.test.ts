import { test } from "uvu";
import assert from "uvu/assert";

import { isDescendant, leaf, parent } from "../src/lib/account";

test("account: split account names", () => {
  assert.is(parent("asd:asdf"), "asd");
  assert.is(parent("asd"), "");
  assert.is(parent(""), "");
  assert.is(leaf("asd:asdf"), "asdf");
  assert.is(leaf("asd"), "asd");
  assert.is(leaf(""), "");
});

test("account: check whether account is descendant of another", () => {
  assert.is(true, isDescendant("A", ""));
  assert.is(true, isDescendant("A:Test", ""));
  assert.is(true, isDescendant("A", "A"));
  assert.is(true, isDescendant("A:Test", "A"));
  assert.is(false, isDescendant("ATest", "A"));
});

test.run();
