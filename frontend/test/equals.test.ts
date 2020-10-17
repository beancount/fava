import test from "ava";

import { shallow_equal } from "../src/lib/equals";

test("shallow array equality", (t) => {
  t.assert(shallow_equal([], []));
  t.assert(shallow_equal(["asdf", 1], ["asdf", 1]));
  t.assert(!shallow_equal([1, "asdf"], ["asdf", 1]));
  t.assert(shallow_equal(["asdf"], ["asdf"]));
  const obj = {};
  t.assert(shallow_equal([obj], [obj]));
});
