import { join } from "node:path";

import type { Tree } from "@lezer/common";
import { TreeFragment } from "@lezer/common";
import { test } from "uvu";
import assert from "uvu/assert";
import TSParser from "web-tree-sitter";

import {
  input_edit_for_fragments,
  LezerTSParser,
} from "../src/codemirror/tree-sitter-parser";
import { is_non_empty } from "../src/lib/array";

async function load(): Promise<TSParser> {
  await TSParser.init();
  const path = join(
    __dirname,
    "..",
    "src",
    "codemirror",
    "tree-sitter-beancount.wasm",
  );
  const lang = await TSParser.Language.load(path);
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
  assert.ok(edit);
  assert.equal(edit.startIndex, 314);
  assert.equal(edit.oldEndIndex, 733);
  assert.equal(edit.newEndIndex, 315);
});

test("deduce an deletion at the start", () => {
  const edit = input_edit_for_fragments(
    [new TreeFragment(0, 418, { length: 733 } as Tree, 315, true, false)],
    315,
  );
  assert.ok(edit);
  assert.equal(edit.startIndex, 0);
  assert.equal(edit.oldEndIndex, 316);
  assert.equal(edit.newEndIndex, 1);
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
  assert.ok(edit);
  assert.equal(edit.startIndex, 163);
  assert.equal(edit.oldEndIndex, 476);
  assert.equal(edit.newEndIndex, 165);
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
  assert.ok(edit);
  assert.equal(edit.startIndex, 163);
  assert.equal(edit.oldEndIndex, 165);
  assert.equal(edit.newEndIndex, 476);
});

test("parse that reuses a single fragment", async () => {
  const ts_parser = await load();
  const parser = new LezerTSParser(ts_parser, [], "beancount_file");
  const line = "2012-12-12 price USD 1 EUR\n";
  const tree = parser.parse(line + line);
  assert.equal(tree.length, line.length * 2);
  assert.snapshot(
    tree_string(tree),
    "beancount_file(price(date,PRICE,currency,amount(number,currency)),price(date,PRICE,currency,amount(number,currency)))",
  );
  let fragments = TreeFragment.addTree(tree);
  fragments = TreeFragment.applyChanges(fragments, [
    { fromA: 0, toA: line.length, fromB: 0, toB: 0 },
  ]);
  assert.equal(fragments.length, 1);
  assert.ok(is_non_empty(fragments));
  const edit = input_edit_for_fragments(fragments, line.length);
  assert.equal(edit?.startIndex, 0);
  assert.equal(edit?.oldEndIndex, line.length + 1);
  assert.equal(edit?.newEndIndex, 1);
  const new_tree = parser.parse(line, fragments);
  assert.snapshot(
    tree_string(new_tree),
    "beancount_file(price(date,PRICE,currency,amount(number,currency)))",
  );
});

test("parse a single price directive", async () => {
  const ts_parser = await load();
  const parser = new LezerTSParser(ts_parser, [], "beancount_file");
  const line = "2012-12-12 price USD 1 EUR\n";
  const tree = parser.parse(line);
  assert.snapshot(
    tree_string(tree),
    "beancount_file(price(date,PRICE,currency,amount(number,currency)))",
  );

  const partial_parse = parser.startParse(line);
  // Advance directly returns the tree.
  assert.ok(partial_parse.advance());
});

test.run();
