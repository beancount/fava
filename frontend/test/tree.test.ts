import test from "ava";
import { entriesToTree, leafAccount, parentAccount } from "../src/lib/tree";

test("split account names", (t) => {
  t.is(parentAccount("asd:asdf"), "asd");
  t.is(parentAccount("asd"), "");
  t.is(parentAccount(""), "");
  t.is(leafAccount("asd:asdf"), "asdf");
  t.is(leafAccount("asd"), "asd");
  t.is(leafAccount(""), "");
});

test("tree from documents", (t) => {
  t.snapshot(entriesToTree([]));
  const node = { account: "Assets:Cash" };
  t.snapshot(entriesToTree([node]));
});
