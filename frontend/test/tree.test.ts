import { deepEqual } from "node:assert/strict";
import { test } from "node:test";

import { stratify, stratifyAccounts } from "../src/lib/tree.ts";

test("tree: stratifyAccounts", () => {
  const empty = stratifyAccounts(
    [],
    () => "",
    () => null,
  );
  deepEqual(empty, { children: [] });
  const emptyWithData = stratifyAccounts(
    [],
    () => "",
    () => ({ test: "test" }),
  );
  deepEqual(emptyWithData, { children: [], test: "test" });
  const tree = stratifyAccounts(
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
    stratifyAccounts(
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

test("tree: stratify", () => {
  const empty = stratify(
    [],
    () => "",
    () => null,
    (s) => slash_parent(s),
  );
  deepEqual(empty, { children: [] });
  const emptyWithData = stratify(
    [],
    () => "",
    () => ({ test: "test" }),
    (s) => slash_parent(s),
  );
  deepEqual(emptyWithData, { children: [], test: "test" });
  const tree = stratify(
    ["aName/cName", "aName", "aName/bName"],
    (s) => s,
    (name) => ({ name }),
    (s) => slash_parent(s),
  );

  deepEqual(tree, {
    children: [
      {
        children: [
          { children: [], name: "aName/cName" },
          { children: [], name: "aName/bName" },
        ],
        name: "aName",
      },
    ],
    name: "",
  });
  deepEqual(
    stratify(
      ["Assets/Cash"],
      (s) => s,
      (name) => ({ name }),
      (s) => slash_parent(s),
    ),
    {
      children: [
        {
          children: [{ children: [], name: "Assets/Cash" }],
          name: "Assets",
        },
      ],
      name: "",
    },
  );
});

function slash_parent(name: string): string {
  const parent_end = name.lastIndexOf("/");
  return parent_end > 0 ? name.slice(0, parent_end) : "";
}
