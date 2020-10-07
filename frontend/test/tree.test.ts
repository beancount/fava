import test from "ava";
import { entriesToTree, leafAccount, parentAccount } from "../src/lib/tree";

test("split account names", (t) => {
  t.deepEqual(parentAccount("asd:asdf"), "asd");
  t.deepEqual(parentAccount("asd"), "");
  t.deepEqual(parentAccount(""), "");
  t.deepEqual(leafAccount("asd:asdf"), "asdf");
  t.deepEqual(leafAccount("asd"), "asd");
  t.deepEqual(leafAccount(""), "");
});

test("tree from documents", (t) => {
  t.snapshot(entriesToTree([]));
  const node = { account: "Assets:Cash" };
  t.snapshot(entriesToTree([node]));
});
