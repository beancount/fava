import test from "ava";
import { entriesToTree, Node } from "../src/documents/util";

test("tree from documents", (t) => {
  const root: Node = { name: "", fullname: "", children: new Map() };
  t.deepEqual(entriesToTree([]), root);
  const node = { account: "Assets:Cash" };
  const assetsNode: Node = {
    name: "Assets",
    fullname: "Assets",
    children: new Map(),
  };
  root.children.set("Assets", assetsNode);
  const assetsCashNode: Node = {
    name: "Cash",
    fullname: "Assets:Cash",
    children: new Map(),
  };
  assetsNode.children.set("Cash", assetsCashNode);
  t.deepEqual(entriesToTree([node]), root);
});
