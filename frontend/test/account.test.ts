import test from "ava";

import { isDescendant, leaf, parent } from "../src/lib/account";

test("account: split account names", (t) => {
  t.is(parent("asd:asdf"), "asd");
  t.is(parent("asd"), "");
  t.is(parent(""), "");
  t.is(leaf("asd:asdf"), "asdf");
  t.is(leaf("asd"), "asd");
  t.is(leaf(""), "");
});

test("account: check whether account is descendant of another", (t) => {
  t.true(isDescendant("A", ""));
  t.true(isDescendant("A:Test", ""));
  t.true(isDescendant("A", "A"));
  t.true(isDescendant("A:Test", "A"));
  t.false(isDescendant("ATest", "A"));
});
