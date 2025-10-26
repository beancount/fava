import { equal, ok } from "node:assert/strict";
import { join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

import type { Tree } from "@lezer/common";
import { TreeFragment } from "@lezer/common";
import { Language as TSLanguage, Parser as TSParser } from "web-tree-sitter";

import {
  input_edit_for_fragments,
  LezerTSParser,
} from "../src/codemirror/tree-sitter-parser.ts";
import { is_non_empty } from "../src/lib/array.ts";

async function load(): Promise<TSParser> {
  await TSParser.init();
  const path = join(
    fileURLToPath(import.meta.url),
    "..",
    "..",
    "src",
    "codemirror",
    "tree-sitter-beancount.wasm",
  );
  const lang = await TSLanguage.load(path);
  const parser = new TSParser();
  parser.setLanguage(lang);
  return parser;
}
// eslint-disable-next-line @typescript-eslint/no-base-to-string
const tree_string = (t: Tree) => t.toString();

test("deduce an deletion at the end", () => {
  const edit = input_edit_for_fragments(
    [new TreeFragment(0, 315, { length: 733 } as Tree, 0, false, true)],
    315,
  );
  ok(edit);
  equal(edit.startIndex, 314);
  equal(edit.oldEndIndex, 733);
  equal(edit.newEndIndex, 315);
});

test("deduce an deletion at the start", () => {
  const edit = input_edit_for_fragments(
    [new TreeFragment(0, 418, { length: 733 } as Tree, 315, true, false)],
    315,
  );
  ok(edit);
  equal(edit.startIndex, 0);
  equal(edit.oldEndIndex, 316);
  equal(edit.newEndIndex, 1);
});

test("deduce a deletion in the middle", () => {
  const tree = { length: 733 } as Tree;
  const edit = input_edit_for_fragments(
    [
      new TreeFragment(0, 164, tree, 0, false, true),
      new TreeFragment(164, 422, tree, 311, true, false),
    ],
    422,
  );
  ok(edit);
  equal(edit.startIndex, 163);
  equal(edit.oldEndIndex, 476);
  equal(edit.newEndIndex, 165);
});

test("deduce an insertion in the middle", () => {
  const tree = { length: 422 } as Tree;
  const edit = input_edit_for_fragments(
    [
      new TreeFragment(0, 164, tree, 0, false, true),
      new TreeFragment(475, 733, tree, -311, true, false),
    ],
    733,
  );
  ok(edit);
  equal(edit.startIndex, 163);
  equal(edit.oldEndIndex, 165);
  equal(edit.newEndIndex, 476);
});

test("parse that reuses a single fragment", async () => {
  const ts_parser = await load();
  const parser = new LezerTSParser(ts_parser, [], "beancount_file");
  const line = "2012-12-12 price USD 1 EUR\n";
  const tree = parser.parse(line + line);
  equal(tree.length, line.length * 2);
  equal(
    tree_string(tree),
    "beancount_file(price(date,PRICE,currency,amount(number,currency)),price(date,PRICE,currency,amount(number,currency)))",
  );
  let fragments = TreeFragment.addTree(tree);
  fragments = TreeFragment.applyChanges(fragments, [
    { fromA: 0, toA: line.length, fromB: 0, toB: 0 },
  ]);
  equal(fragments.length, 1);
  ok(is_non_empty(fragments));
  const edit = input_edit_for_fragments(fragments, line.length);
  equal(edit?.startIndex, 0);
  equal(edit.oldEndIndex, line.length + 1);
  equal(edit.newEndIndex, 1);
  const new_tree = parser.parse(line, fragments);
  equal(
    tree_string(new_tree),
    "beancount_file(price(date,PRICE,currency,amount(number,currency)))",
  );
});

test("parse a single price directive", async () => {
  const ts_parser = await load();
  const parser = new LezerTSParser(ts_parser, [], "beancount_file");
  const line = "2012-12-12 price USD 1 EUR\n";
  const tree = parser.parse(line);
  equal(
    tree_string(tree),
    "beancount_file(price(date,PRICE,currency,amount(number,currency)))",
  );

  const partial_parse = parser.startParse(line);
  // Advance directly returns the tree.
  ok(partial_parse.advance());
});
