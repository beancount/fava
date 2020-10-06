import test from "ava";
import { entriesToTree, Node } from "../src/documents/util";

const n = (name: string, fullname: string): Node => ({
  name,
  fullname,
  children: new Map<string, Node>(),
});

test("tree from documents", (t) => {
  const root = n("", "");
  t.deepEqual(entriesToTree([]), root);
  const node = { account: "Assets:Cash" };
  const assetsNode = n("Assets", "Assets");
  root.children.set("Assets", assetsNode);
  const assetsCashNode = n("Cash", "Assets:Cash");
  assetsNode.children.set("Cash", assetsCashNode);
  t.deepEqual(entriesToTree([node]), root);
});
