import { test } from "uvu";
import assert from "uvu/assert";

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
  assert.equal(boolean(true).unwrap(), true);
  assert.equal(boolean(false).unwrap(), false);
  assert.ok(boolean({ a: 1 }).is_err);
  assert.ok(boolean("1").is_err);
});

test("validate constant", () => {
  assert.is(constant(true)(true).unwrap(), true);
  assert.is(constant(1)(1).unwrap(), 1);
  assert.ok(constant(1)("1").is_err);
  assert.ok(constant(1)(4).is_err);
  assert.ok(constant("1")(1).is_err);
});

test("validate date", () => {
  const d = new Date("2012-12-12");
  assert.is(+date("2012-12-12").unwrap(), +d);
  assert.equal(date(d).unwrap(), d);
  assert.ok(date("2-40").is_err);
  assert.ok(date("").is_err);
  assert.ok(date("2012-12-40").is_err);
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
