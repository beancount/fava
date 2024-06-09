import { test } from "uvu";
import assert from "uvu/assert";

import { is_non_empty, last_element } from "../src/lib/array";
import { errorWithCauses } from "../src/lib/errors";
import { getInterval } from "../src/lib/interval";
import { parseJSON } from "../src/lib/json";

test("validate interval", () => {
  assert.equal(getInterval("year"), "year");
  assert.equal(getInterval("yasdfaear"), "month");
});

test("parse json", () => {
  assert.equal(parseJSON("{}").unwrap(), {});

  const invalid = parseJSON("invalid").unwrap_err();
  assert.instance(invalid, SyntaxError);
});

test("non-empty array helpers", () => {
  assert.is(is_non_empty([]), false);
  const a = [false, true];
  assert.ok(is_non_empty(a));
  assert.is(last_element(a), true);
});

test("print out error with causes", () => {
  const err1 = new Error("a reason");
  const err2 = new Error("b reason", { cause: err1 });

  assert.equal(errorWithCauses(err1), "a reason");
  assert.equal(errorWithCauses(err2), "b reason\n  Caused by: a reason");
});

test.run();
