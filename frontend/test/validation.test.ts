import { test } from "uvu";
import assert from "uvu/assert";

import { ok } from "../src/lib/result";
import {
  boolean,
  constant,
  date,
  number,
  object,
  optional_string,
  record,
  string,
} from "../src/lib/validation";

test("validate boolean", () => {
  assert.equal(boolean(true), ok(true));
  assert.equal(boolean(false), ok(false));
  assert.is(false, boolean({ a: 1 }).success);
  assert.is(false, boolean("1").success);
});

test("validate constant", () => {
  assert.ok(constant(true)(true));
  assert.ok(constant(1)(1));
  assert.is(false, constant(1)("1").success);
  assert.is(false, constant(1)(4).success);
  assert.is(false, constant("1")(1).success);
});

test("validate date", () => {
  const d = new Date("2012-12-12");
  assert.is(+date("2012-12-12").value, +d);
  assert.equal(date(d), ok(d));
  assert.is(false, date("2-40").success);
  assert.is(false, date("").success);
  assert.is(false, date("2012-12-40").success);
});

test("validate number", () => {
  assert.equal(number(1), ok(1));
  assert.is(false, number({ a: 1 }).success);
  assert.is(false, number("1").success);
});

test("validate string", () => {
  assert.equal(string("test"), ok("test"));
  assert.is(false, string({ a: 1 }).success);
  assert.is(false, string(1).success);
});

test("validate optional string", () => {
  assert.ok(optional_string(null).value === "");
  assert.ok(optional_string({}).value === "");
  assert.ok(optional_string("asdf").value === "asdf");
});

test("validate Record<>", () => {
  const strRecord = record(string);
  assert.equal(strRecord({}), ok({}));
  assert.equal(strRecord({ a: "test" }), ok({ a: "test" }));
  assert.is(false, strRecord({ a: 1 }).success);
});

test("validate object", () => {
  const val = object({ str: string, num: number });
  assert.equal(
    val({ str: "str", num: 1, extra: 1 }),
    ok({ str: "str", num: 1 })
  );
  assert.equal(val({ str: "str", num: 1 }), ok({ str: "str", num: 1 }));
  assert.is(false, val({ str: 1 }).success);
  assert.is(false, val(1).success);
});

test.run();
