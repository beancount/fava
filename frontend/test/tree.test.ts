import test from "ava";
import {
  entriesToTree,
  leafAccount,
  parentAccount,
  stratify,
} from "../src/lib/tree";

test("split account names", (t) => {
  t.is(parentAccount("asd:asdf"), "asd");
  t.is(parentAccount("asd"), "");
  t.is(parentAccount(""), "");
  t.is(leafAccount("asd:asdf"), "asdf");
  t.is(leafAccount("asd"), "asd");
  t.is(leafAccount(""), "");
});

test("tree: stratify", (t) => {
  const empty = stratify(
    [],
    () => "",
    () => null
  );
  t.deepEqual(empty, { children: [] });
  const emptyWithData = stratify(
    [],
    () => "",
    () => ({ test: "test" })
  );
  t.deepEqual(emptyWithData, { children: [], test: "test" });
  const tree = stratify(
    ["aName:cName", "aName", "aName:bName"],
    (s) => s,
    (name) => ({ name })
  );
  t.snapshot(tree);
});

test("tree from documents", (t) => {
  t.deepEqual(entriesToTree([]), { children: [], name: "" });
  t.snapshot(entriesToTree([{ account: "Assets:Cash" }]));
});
