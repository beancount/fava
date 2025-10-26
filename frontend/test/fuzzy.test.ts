import { deepEqual, ok } from "node:assert/strict";
import { test } from "node:test";

import { fuzzyfilter, fuzzytest, fuzzywrap } from "../src/lib/fuzzy.ts";

test("fuzzy test", () => {
  ok(fuzzytest("asdf", "asdfasdf"));
  ok(fuzzytest("asdf", "ASDFASDF"));
  // "smart-case" matching
  ok(fuzzytest("Asdf", "ASDFASDF") < fuzzytest("asdf", "ASDFASDF"));
  ok(fuzzytest("ASDF", "ASDFASDF") === fuzzytest("asdf", "ASDFASDF"));

  ok(!fuzzytest("Asdf", "asdfasdf"));
  ok(fuzzytest("asdf", "a;lks;lk;lkd;lk;flkj;l"));
  ok(!fuzzytest("asdf", "sdfsdf"));
  ok(!fuzzytest("a", "sdfsdf"));
});

test("fuzzy filter", () => {
  deepEqual(fuzzyfilter("", ["asdfasdf", "a"]), ["asdfasdf", "a"]);
  deepEqual(fuzzyfilter("asdf", ["asdfasdf", "nomatch"]), ["asdfasdf"]);
  deepEqual(fuzzyfilter("asdf", ["assdfsdf", "asdfasdf", "nomatch"]), [
    "asdfasdf",
    "assdfsdf",
  ]);
  deepEqual(
    fuzzyfilter("asdf", [
      "test",
      "asdfasdf",
      "asdxf",
      "asxxdf",
      "nomatch",
      "asdf",
    ]),
    ["asdfasdf", "asdf", "asdxf", "asxxdf"],
  );
});

test("fuzzy wap", () => {
  deepEqual(fuzzywrap("", "tenotest"), [["text", "tenotest"]]);
  deepEqual(fuzzywrap("", "<>tenotest"), [["text", "<>tenotest"]]);

  deepEqual(fuzzywrap("test", "tenotest"), [
    ["text", "teno"],
    ["match", "test"],
  ]);
  // no match for case sensitive pattern:
  deepEqual(fuzzywrap("tesT", "test"), [["text", "test"]]);
  deepEqual(fuzzywrap("sdf", "nomatch"), [["text", "nomatch"]]);
  deepEqual(fuzzywrap("test", "tetest"), [
    ["text", "te"],
    ["match", "test"],
  ]);
  deepEqual(fuzzywrap("test", "teTEST"), [
    ["text", "te"],
    ["match", "TEST"],
  ]);
  deepEqual(fuzzywrap("a", "asdfasdf"), [
    ["match", "a"],
    ["text", "sdfasdf"],
  ]);
  deepEqual(fuzzywrap("as", "asdfasdf"), [
    ["match", "as"],
    ["text", "dfasdf"],
  ]);
  deepEqual(fuzzywrap("as", "as"), [["match", "as"]]);
  deepEqual(fuzzywrap("te", "tae"), [
    ["match", "t"],
    ["text", "a"],
    ["match", "e"],
  ]);
  deepEqual(fuzzywrap("te", "ta<e"), [
    ["match", "t"],
    ["text", "a<"],
    ["match", "e"],
  ]);
  deepEqual(fuzzywrap("as", "<span>as"), [
    ["text", "<span>"],
    ["match", "as"],
  ]);
});
