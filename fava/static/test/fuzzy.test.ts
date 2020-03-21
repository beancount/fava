import test from "ava";
import { fuzzytest } from "../javascript/lib/fuzzy";

test("fuzzy test", t => {
  t.assert(fuzzytest("asdf", "asdfasdf"));
  t.assert(fuzzytest("asdf", "a;lks;lk;lkd;lk;flkj;l"));
  t.assert(!fuzzytest("asdf", "sdfsdf"));
});
