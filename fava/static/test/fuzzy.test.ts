import test from "ava";
import { fuzzytest, fuzzywrap } from "../javascript/lib/fuzzy";

test("fuzzy test", t => {
  t.assert(fuzzytest("asdf", "asdfasdf"));
  t.assert(fuzzytest("asdf", "ASDFASDF"));
  t.assert(fuzzytest("Asdf", "ASDFASDF"));
  t.assert(!fuzzytest("Asdf", "asdfasdf"));
  t.assert(fuzzytest("asdf", "a;lks;lk;lkd;lk;flkj;l"));
  t.assert(!fuzzytest("asdf", "sdfsdf"));
  t.assert(!fuzzytest("a", "sdfsdf"));
});

test("fuzzy wap", t => {
  t.deepEqual(fuzzywrap("sdf", "nomatch"), "nomatch");
  t.deepEqual(fuzzywrap("a", "asdfasdf"), "<span>a</span>sdfasdf");
  t.deepEqual(fuzzywrap("as", "asdfasdf"), "<span>as</span>dfasdf");
  t.deepEqual(fuzzywrap("as", "as"), "<span>as</span>");
});
