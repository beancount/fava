import { test } from "uvu";
import assert from "uvu/assert";

import type { Result } from "../src/lib/result";
import { collect, Err, err, Ok, ok } from "../src/lib/result";

test("basic result operations", () => {
  const obj = { a: "a" };
  const ok_obj = ok(obj);
  assert.instance(ok_obj, Ok);
  assert.is(ok_obj.is_ok, true);
  assert.is(ok_obj.is_err, false);
  assert.is(ok_obj.or_else(), ok_obj);
  assert.is(ok_obj.unwrap(), obj);
  assert.is(ok_obj.unwrap_or(), obj);
  assert.throws(() => ok_obj.unwrap_err());
  assert.is(ok_obj.and_then((obj) => ok(obj.a)).unwrap(), "a");

  const err_obj: Result<unknown, unknown> = err(obj);
  assert.instance(err_obj, Err);
  assert.is(err_obj.is_ok, false);
  assert.is(err_obj.is_err, true);
  assert.is(err_obj.and_then(), err_obj);
  assert.is(err_obj.unwrap_err(), obj);
  assert.is(err_obj.unwrap_or(null), null);
  assert.throws(() => err_obj.unwrap());
});

test("collect results", () => {
  const a = ok("a");
  const b = ok("b");
  assert.equal(collect([a, b]), ok(["a", "b"]));

  const e = err("e");
  assert.is(collect([a, b, e]), e);
});

test.run();
