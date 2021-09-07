import { test } from "uvu";
import assert from "uvu/assert";

import { fuzzyfilter, fuzzytest, fuzzywrap } from "../src/lib/fuzzy";

test("fuzzy test", () => {
  assert.ok(fuzzytest("asdf", "asdfasdf"));
  assert.ok(fuzzytest("asdf", "ASDFASDF"));
  // "smart-case" matching
  assert.ok(fuzzytest("Asdf", "ASDFASDF") < fuzzytest("asdf", "ASDFASDF"));
  assert.ok(fuzzytest("ASDF", "ASDFASDF") === fuzzytest("asdf", "ASDFASDF"));

  assert.ok(!fuzzytest("Asdf", "asdfasdf"));
  assert.ok(fuzzytest("asdf", "a;lks;lk;lkd;lk;flkj;l"));
  assert.ok(!fuzzytest("asdf", "sdfsdf"));
  assert.ok(!fuzzytest("a", "sdfsdf"));
});

test("fuzzy filter", () => {
  assert.equal(fuzzyfilter("", ["asdfasdf", "a"]), ["asdfasdf", "a"]);
  assert.equal(fuzzyfilter("asdf", ["asdfasdf", "nomatch"]), ["asdfasdf"]);
  assert.equal(fuzzyfilter("asdf", ["assdfsdf", "asdfasdf", "nomatch"]), [
    "asdfasdf",
    "assdfsdf",
  ]);
  assert.equal(
    fuzzyfilter("asdf", [
      "test",
      "asdfasdf",
      "asdxf",
      "asxxdf",
      "nomatch",
      "asdf",
    ]),
    ["asdfasdf", "asdf", "asdxf", "asxxdf"]
  );
});

test("fuzzy wap", () => {
  assert.is(fuzzywrap("", "tenotest"), "tenotest");
  assert.is(fuzzywrap("test", "tenotest"), "teno<span>test</span>");
  assert.is(fuzzywrap("sdf", "nomatch"), "nomatch");
  assert.is(fuzzywrap("test", "tetest"), "te<span>test</span>");
  assert.is(fuzzywrap("test", "teTEST"), "te<span>TEST</span>");
  assert.is(fuzzywrap("a", "asdfasdf"), "<span>a</span>sdfasdf");
  assert.is(fuzzywrap("as", "asdfasdf"), "<span>as</span>dfasdf");
  assert.is(fuzzywrap("as", "as"), "<span>as</span>");
});

test.run();
