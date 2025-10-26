import { deepEqual, equal, ok } from "node:assert/strict";
import { test } from "node:test";

import { is_non_empty, last_element } from "../src/lib/array.ts";
import { errorWithCauses } from "../src/lib/errors.ts";
import { getInterval } from "../src/lib/interval.ts";
import { parseJSON } from "../src/lib/json.ts";

test("validate interval", () => {
  equal(getInterval("year"), "year");
  equal(getInterval("yasdfaear"), "month");
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

test("print out error with causes", () => {
  const err1 = new Error("a reason");
  const err2 = new Error("b reason", { cause: err1 });

  equal(errorWithCauses(err1), "a reason");
  equal(errorWithCauses(err2), "b reason\n  Caused by: a reason");
});
