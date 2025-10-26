import { deepEqual, equal, ok } from "node:assert/strict";
import { test } from "node:test";

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
} from "../src/lib/validation.ts";

test("validate boolean", () => {
  equal(boolean(true).unwrap(), true);
  equal(boolean(false).unwrap(), false);
  ok(boolean({ a: 1 }).is_err);
  ok(boolean("1").unwrap_err() instanceof PrimitiveValidationError);
});

test("validate constant", () => {
  equal(constant(true)(true).unwrap(), true);
  equal(constant(1)(1).unwrap(), 1);
  ok(constant(1)("1").is_err);
  ok(constant(1)(4).is_err);
  ok(constant("1")(1).is_err);
});

test("validate constants", () => {
  equal(constants(true)(true).unwrap(), true);
  equal(constants(1)(1).unwrap(), 1);
  ok(constants(1)("1").is_err);
  ok(constants(1)(4).is_err);
  ok(constants("1")(1).is_err);
  equal(constants("a", "b")("a").unwrap(), "a");

  const a_or_b = constants("a", "b");
  const a: "a" | "b" = a_or_b("a").unwrap();
  equal(a, "a");
  equal(a_or_b("b").unwrap(), "b");
  ok(a_or_b("c").is_err);
});

test("validate tagged union", () => {
  const a_or_b = tagged_union("t", {
    a: object({ a: boolean }),
    b: object({ b: boolean }),
  });
  deepEqual(a_or_b({ t: "a", a: true }).unwrap(), { a: true });
  ok(a_or_b({ t: "a", b: true }).is_err);
  const err = a_or_b({ t: "a", b: true });
  ok(err.is_err);
  ok(err.error instanceof ValidationError);
  ok(err.error.cause instanceof ValidationError);

  deepEqual(a_or_b({ t: "b", b: true }).unwrap(), { b: true });

  ok(a_or_b(null).is_err);
  ok(a_or_b({}).is_err);
  ok(a_or_b({ t: "c" }).is_err);
  ok(a_or_b({ t: "a" }).is_err);
});

test("validate date", () => {
  const d = new Date("2012-12-12");
  equal(+date("2012-12-12").unwrap(), +d);
  deepEqual(date(d).unwrap(), d);
  ok(date("2-40").is_err);
  ok(date("").is_err);
  ok(date("2012-12-40").is_err);
  ok(date("2012-12-20T20:00").is_err);
});

test("validate number", () => {
  equal(number(1).unwrap(), 1);
  ok(number({ a: 1 }).is_err);
  ok(number("1").is_err);
});

test("validate string", () => {
  equal(string("test").unwrap(), "test");
  ok(string({ a: 1 }).is_err);
  ok(string(1).is_err);
});

test("validate optional string", () => {
  ok(optional_string(null).value === "");
  ok(optional_string({}).value === "");
  ok(optional_string("asdf").value === "asdf");
});

test("validate tuple", () => {
  const string_and_boolean = tuple(string, boolean);
  deepEqual(string_and_boolean(["asdf", false]).unwrap(), ["asdf", false]);
  ok(string_and_boolean([false, "asdf"]).is_err);
  ok(string_and_boolean([]).is_err);

  const string_boolean_boolean = tuple(string, boolean, boolean);
  deepEqual(string_boolean_boolean(["asdf", false, false]).unwrap(), [
    "asdf",
    false,
    false,
  ]);
  ok(string_boolean_boolean([false, "asdf"]).is_err);
  ok(string_boolean_boolean([]).is_err);
});

test("validate Record<>", () => {
  const strRecord = record(string);
  deepEqual(strRecord({}).unwrap(), {});
  deepEqual(strRecord({ a: "test" }).unwrap(), { a: "test" });
  ok(strRecord({ a: 1 }).is_err);
});

test("validate object", () => {
  const val = object({ str: string, num: number });
  deepEqual(val({ str: "str", num: 1, extra: 1 }).unwrap(), {
    str: "str",
    num: 1,
  });
  deepEqual(val({ str: "str", num: 1 }).unwrap(), { str: "str", num: 1 });
  ok(val({ str: 1 }).is_err);
  ok(val(1).is_err);
});
