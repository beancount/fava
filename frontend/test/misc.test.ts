import { deepEqual, equal, ok } from "node:assert/strict";
import { test } from "node:test";

import { is_non_empty, last_element, move } from "../src/lib/array.ts";
import { shallow_equal } from "../src/lib/equals.ts";
import { errorWithCauses } from "../src/lib/errors.ts";
import { getInterval } from "../src/lib/interval.ts";
import { parseJSON } from "../src/lib/json.ts";
import { is_empty } from "../src/lib/objects.ts";
import { toggle } from "../src/lib/set.ts";

test("move array elements", () => {
  const initital = [0, 1, 2, 3];
  const moved = move(initital, 1, 2);
  deepEqual(moved, [0, 2, 1, 3]);
  deepEqual(initital, [0, 1, 2, 3]);
});

test("shallow array equality", () => {
  ok(shallow_equal([], []));
  ok(shallow_equal(["asdf", 1], ["asdf", 1]));
  ok(!shallow_equal([1, "asdf"], ["asdf", 1]));
  ok(shallow_equal(["asdf"], ["asdf"]));
});

test("validate interval", () => {
  equal(getInterval("year"), "year");
  equal(getInterval("yasdfaear"), "month");
});

test("check whether objects are empty", () => {
  ok(is_empty({}));
  equal(is_empty({ asdf: "asdf" }), false);
});

test("parse json", () => {
  deepEqual(parseJSON("{}").unwrap(), {});

  const invalid = parseJSON("invalid").unwrap_err();
  ok(invalid instanceof SyntaxError);
});

test("non-empty array helpers", () => {
  equal(is_non_empty([]), false);
  const a = [false, true];
  ok(is_non_empty(a));
  equal(last_element(a), true);
});

test("toggle set elements", () => {
  deepEqual(toggle(new Set([0, 1]), 0), new Set([1]));
  deepEqual(toggle(new Set(["0", 1]), 0), new Set(["0", 0, 1]));
  deepEqual(toggle(new Set([0, 1]), 2), new Set([0, 1, 2]));
});

test("print out error with causes", () => {
  const err1 = new Error("a reason");
  const err2 = new Error("b reason", { cause: err1 });

  equal(errorWithCauses(err1), "a reason");
  equal(errorWithCauses(err2), "b reason\n  Caused by: a reason");
});
