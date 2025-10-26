import { deepEqual, equal, ok, throws } from "node:assert/strict";

import { test } from "uvu";

import type { Result } from "../src/lib/result.ts";
import { collect, Err, err, Ok, ok as res_ok } from "../src/lib/result.ts";

test("basic result operations", () => {
  const obj = { a: "a" };
  const ok_obj = res_ok(obj);
  ok(ok_obj instanceof Ok);
  equal(ok_obj.is_ok, true);
  equal(ok_obj.is_err, false);
  equal(ok_obj.or_else(), ok_obj);
  equal(ok_obj.unwrap(), obj);
  equal(ok_obj.unwrap_or(), obj);
  throws(() => ok_obj.unwrap_err());
  equal(ok_obj.and_then((obj) => res_ok(obj.a)).unwrap(), "a");

  const err_obj: Result<unknown, unknown> = err(obj);
  ok(err_obj instanceof Err);
  equal(err_obj.is_ok, false);
  equal(err_obj.is_err, true);
  equal(err_obj.and_then(), err_obj);
  equal(err_obj.unwrap_err(), obj);
  equal(err_obj.unwrap_or(null), null);
  throws(() => err_obj.unwrap());
});

test("collect results", () => {
  const a = res_ok("a");
  const b = res_ok("b");
  deepEqual(collect([a, b]), res_ok(["a", "b"]));

  const e = err("e");
  equal(collect([a, b, e]), e);
});

test.run();
