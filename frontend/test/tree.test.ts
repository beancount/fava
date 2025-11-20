import { deepEqual } from "node:assert/strict";
import { test } from "node:test";

import { stratify } from "../src/lib/tree.ts";

test("tree: stratify", () => {
  const empty = stratify(
    [],
    () => "",
    () => null,
  );
  deepEqual(empty, { children: [] });
  const emptyWithData = stratify(
    [],
    () => "",
    () => ({ test: "test" }),
  );
  deepEqual(emptyWithData, { children: [], test: "test" });
  const tree = stratify(
    ["aName:cName", "aName", "aName:bName"],
    (s) => s,
    (name) => ({ name }),
  );

  deepEqual(tree, {
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
  deepEqual(
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
