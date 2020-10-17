import test from "ava";

import { leaf, parent } from "../src/lib/account";

test("split account names", (t) => {
  t.is(parent("asd:asdf"), "asd");
  t.is(parent("asd"), "");
  t.is(parent(""), "");
  t.is(leaf("asd:asdf"), "asdf");
  t.is(leaf("asd"), "asd");
  t.is(leaf(""), "");
});
