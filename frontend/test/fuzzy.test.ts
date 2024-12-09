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
    ["asdfasdf", "asdf", "asdxf", "asxxdf"],
  );
});

test("fuzzy wap", () => {
  assert.equal(fuzzywrap("", "tenotest"), [["text", "tenotest"]]);
  assert.equal(fuzzywrap("", "<>tenotest"), [["text", "<>tenotest"]]);

  assert.equal(fuzzywrap("test", "tenotest"), [
    ["text", "teno"],
    ["match", "test"],
  ]);
  // no match for case sensitive pattern:
  assert.equal(fuzzywrap("tesT", "test"), [["text", "test"]]);
  assert.equal(fuzzywrap("sdf", "nomatch"), [["text", "nomatch"]]);
  assert.equal(fuzzywrap("test", "tetest"), [
    ["text", "te"],
    ["match", "test"],
  ]);
  assert.equal(fuzzywrap("test", "teTEST"), [
    ["text", "te"],
    ["match", "TEST"],
  ]);
  assert.equal(fuzzywrap("a", "asdfasdf"), [
    ["match", "a"],
    ["text", "sdfasdf"],
  ]);
  assert.equal(fuzzywrap("as", "asdfasdf"), [
    ["match", "as"],
    ["text", "dfasdf"],
  ]);
  assert.equal(fuzzywrap("as", "as"), [["match", "as"]]);
  assert.equal(fuzzywrap("te", "tae"), [
    ["match", "t"],
    ["text", "a"],
    ["match", "e"],
  ]);
  assert.equal(fuzzywrap("te", "ta<e"), [
    ["match", "t"],
    ["text", "a<"],
    ["match", "e"],
  ]);
  assert.equal(fuzzywrap("as", "<span>as"), [
    ["text", "<span>"],
    ["match", "as"],
  ]);
});

test.run();
