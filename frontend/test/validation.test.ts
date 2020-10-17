import test from "ava";

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
  t.assert(boolean(true));
  t.assert(!boolean(false));
  t.throws(() => boolean({ a: 1 }));
  t.throws(() => boolean("1"));
});

test("validate constant", (t) => {
  t.assert(constant(true)(true));
  t.assert(constant(1)(1));
  t.throws(() => constant(1)("1"));
  t.throws(() => constant(1)(4));
  t.throws(() => constant("1")(1));
});

test("validate date", (t) => {
  const d = new Date("2012-12-12");
  t.is(+date("2012-12-12"), +d);
  t.deepEqual(date(d), d);
  t.throws(() => date("2-40"));
  t.throws(() => date(""));
  t.throws(() => date("2012-12-40"));
});

test("validate number", (t) => {
  t.assert(number(1) === 1);
  t.throws(() => number({ a: 1 }));
  t.throws(() => number("1"));
});

test("validate string", (t) => {
  t.assert(string("test") === "test");
  t.throws(() => string({ a: 1 }));
  t.throws(() => string(1));
});

test("validate optional string", (t) => {
  t.assert(optional_string(null) === "");
  t.assert(optional_string({}) === "");
  t.assert(optional_string("asdf") === "asdf");
});

test("validate Record<>", (t) => {
  const strRecord = record(string);
  t.deepEqual(strRecord({}), {});
  t.deepEqual(strRecord({ a: "test" }), { a: "test" });
  t.throws(() => strRecord({ a: 1 }));
});

test("validate object", (t) => {
  const val = object({ str: string, num: number });
  t.deepEqual(val({ str: "str", num: 1, extra: 1 }), { str: "str", num: 1 });
  t.deepEqual(val({ str: "str", num: 1 }), { str: "str", num: 1 });
  t.throws(() => val({ str: 1 }));
  t.throws(() => val(1));
});
