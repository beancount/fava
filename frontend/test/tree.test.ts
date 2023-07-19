import { test } from "uvu";
import assert from "uvu/assert";

import { stratify } from "../src/lib/tree";

test("tree: stratify", () => {
  const empty = stratify(
    [],
    () => "",
    () => null,
  );
  assert.equal(empty, { children: [] });
  const emptyWithData = stratify(
    [],
    () => "",
    () => ({ test: "test" }),
  );
  assert.equal(emptyWithData, { children: [], test: "test" });
  const tree = stratify(
    ["aName:cName", "aName", "aName:bName"],
    (s) => s,
    (name) => ({ name }),
  );

  assert.equal(tree, {
    children: [
      {
        children: [
          { children: [], name: "aName:bName" },
          { children: [], name: "aName:cName" },
        ],
        name: "aName",
      },
    ],
    name: "",
  });
  assert.equal(
    stratify(
      ["Assets:Cash"],
      (s) => s,
      (name) => ({ name }),
    ),
    {
      children: [
        {
          children: [{ children: [], name: "Assets:Cash" }],
          name: "Assets",
        },
      ],
      name: "",
    },
  );
});

test.run();
