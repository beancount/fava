import { test } from "uvu";
import assert from "uvu/assert";

import { getInterval } from "../src/lib/interval";
import { parseJSON } from "../src/lib/json";

test("validate interval", () => {
  assert.equal(getInterval("year"), "year");
  assert.equal(getInterval("yasdfaear"), "month");
});

test("parse json", () => {
  assert.equal(parseJSON("{}").unwrap(), {});

  const invalid = parseJSON("invalid");
  assert.ok(invalid.is_err && invalid.error.startsWith("JSON syntax error"));
});

test.run();
