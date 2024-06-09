import { test } from "uvu";
import assert from "uvu/assert";

import {
  boolean,
  constant,
  constants,
  date,
  number,
  object,
  optional_string,
  PrimitiveValidationError,
  record,
  string,
  tagged_union,
  tuple,
  ValidationError,
} from "../src/lib/validation";

test("validate boolean", () => {
  assert.equal(boolean(true).unwrap(), true);
  assert.equal(boolean(false).unwrap(), false);
  assert.ok(boolean({ a: 1 }).is_err);
  assert.instance(boolean("1").unwrap_err(), PrimitiveValidationError);
});

test("validate constant", () => {
  assert.is(constant(true)(true).unwrap(), true);
  assert.is(constant(1)(1).unwrap(), 1);
  assert.ok(constant(1)("1").is_err);
  assert.ok(constant(1)(4).is_err);
  assert.ok(constant("1")(1).is_err);
});

test("validate constants", () => {
  assert.is(constants(true)(true).unwrap(), true);
  assert.is(constants(1)(1).unwrap(), 1);
  assert.ok(constants(1)("1").is_err);
  assert.ok(constants(1)(4).is_err);
  assert.ok(constants("1")(1).is_err);
  assert.is(constants("a", "b")("a").unwrap(), "a");

  const a_or_b = constants("a", "b");
  const a: "a" | "b" = a_or_b("a").unwrap();
  assert.is(a, "a");
  assert.is(a_or_b("b").unwrap(), "b");
  assert.ok(a_or_b("c").is_err);
});

test("validate tagged union", () => {
  const a_or_b = tagged_union("t", {
    a: object({ a: boolean }),
    b: object({ b: boolean }),
  });
  assert.equal(a_or_b({ t: "a", a: true }).unwrap(), { a: true });
  assert.ok(a_or_b({ t: "a", b: true }).is_err);
  const err = a_or_b({ t: "a", b: true });
  assert.ok(err.is_err);
  assert.instance(err.error, ValidationError);
  assert.instance(err.error.cause, ValidationError);

  assert.equal(a_or_b({ t: "b", b: true }).unwrap(), { b: true });

  assert.ok(a_or_b(null).is_err);
  assert.ok(a_or_b({}).is_err);
  assert.ok(a_or_b({ t: "c" }).is_err);
  assert.ok(a_or_b({ t: "a" }).is_err);
});

test("validate date", () => {
  const d = new Date("2012-12-12");
  assert.is(+date("2012-12-12").unwrap(), +d);
  assert.equal(date(d).unwrap(), d);
  assert.ok(date("2-40").is_err);
  assert.ok(date("").is_err);
  assert.ok(date("2012-12-40").is_err);
  assert.ok(date("2012-12-20T20:00").is_err);
});

test("validate number", () => {
  assert.equal(number(1).unwrap(), 1);
  assert.ok(number({ a: 1 }).is_err);
  assert.ok(number("1").is_err);
});

test("validate string", () => {
  assert.equal(string("test").unwrap(), "test");
  assert.ok(string({ a: 1 }).is_err);
  assert.ok(string(1).is_err);
});

test("validate optional string", () => {
  assert.ok(optional_string(null).value === "");
  assert.ok(optional_string({}).value === "");
  assert.ok(optional_string("asdf").value === "asdf");
});

test("validate tuple", () => {
  const string_and_boolean = tuple(string, boolean);
  assert.equal(string_and_boolean(["asdf", false]).unwrap(), ["asdf", false]);
  assert.ok(string_and_boolean([false, "asdf"]).is_err);
  assert.ok(string_and_boolean([]).is_err);

  const string_boolean_boolean = tuple(string, boolean, boolean);
  assert.equal(string_boolean_boolean(["asdf", false, false]).unwrap(), [
    "asdf",
    false,
    false,
  ]);
  assert.ok(string_boolean_boolean([false, "asdf"]).is_err);
  assert.ok(string_boolean_boolean([]).is_err);
});

test("validate Record<>", () => {
  const strRecord = record(string);
  assert.equal(strRecord({}).unwrap(), {});
  assert.equal(strRecord({ a: "test" }).unwrap(), { a: "test" });
  assert.ok(strRecord({ a: 1 }).is_err);
});

test("validate object", () => {
  const val = object({ str: string, num: number });
  assert.equal(val({ str: "str", num: 1, extra: 1 }).unwrap(), {
    str: "str",
    num: 1,
  });
  assert.equal(val({ str: "str", num: 1 }).unwrap(), { str: "str", num: 1 });
  assert.ok(val({ str: 1 }).is_err);
  assert.ok(val(1).is_err);
});

test.run();
