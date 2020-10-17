import test from "ava";

import { stratify } from "../src/lib/tree";

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
  t.snapshot(
    stratify(
      ["Assets:Cash"],
      (s) => s,
      (name) => ({ name })
    )
  );
});
