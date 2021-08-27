import test from "ava";

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

test("validate boolean", (t) => {
  t.deepEqual(boolean(true), ok(true));
  t.deepEqual(boolean(false), ok(false));
  t.false(boolean({ a: 1 }).success);
  t.false(boolean("1").success);
});

test("validate constant", (t) => {
  t.assert(constant(true)(true));
  t.assert(constant(1)(1));
  t.false(constant(1)("1").success);
  t.false(constant(1)(4).success);
  t.false(constant("1")(1).success);
});

test("validate date", (t) => {
  const d = new Date("2012-12-12");
  t.is(+date("2012-12-12").value, +d);
  t.deepEqual(date(d), ok(d));
  t.false(date("2-40").success);
  t.false(date("").success);
  t.false(date("2012-12-40").success);
});

test("validate number", (t) => {
  t.deepEqual(number(1), ok(1));
  t.false(number({ a: 1 }).success);
  t.false(number("1").success);
});

test("validate string", (t) => {
  t.deepEqual(string("test"), ok("test"));
  t.false(string({ a: 1 }).success);
  t.false(string(1).success);
});

test("validate optional string", (t) => {
  t.assert(optional_string(null).value === "");
  t.assert(optional_string({}).value === "");
  t.assert(optional_string("asdf").value === "asdf");
});

test("validate Record<>", (t) => {
  const strRecord = record(string);
  t.deepEqual(strRecord({}), ok({}));
  t.deepEqual(strRecord({ a: "test" }), ok({ a: "test" }));
  t.false(strRecord({ a: 1 }).success);
});

test("validate object", (t) => {
  const val = object({ str: string, num: number });
  t.deepEqual(
    val({ str: "str", num: 1, extra: 1 }),
    ok({ str: "str", num: 1 })
  );
  t.deepEqual(val({ str: "str", num: 1 }), ok({ str: "str", num: 1 }));
  t.false(val({ str: 1 }).success);
  t.false(val(1).success);
});
