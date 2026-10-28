import { deepEqual, equal, ok, throws } from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { test } from "node:test";

import {
  DocInput,
  defineLanguageFacet,
  ensureSyntaxTree,
  Language,
} from "@codemirror/language";
import type { ChangeSpec } from "@codemirror/state";
import { EditorState, Text } from "@codemirror/state";
import { NodeType, Tree, TreeFragment } from "@lezer/common";
import * as TS from "web-tree-sitter";

import {
  input_edit_for_fragments,
  LezerTSParser,
} from "../src/codemirror/tree-sitter-parser.ts";
import { is_non_empty } from "../src/lib/array.ts";
import { load_beancount_ts_parser, REPOSITORY_ROOT } from "./helpers.ts";

const ts_parser = await load_beancount_ts_parser();

const parser = new LezerTSParser(ts_parser, [], "beancount_file");

/** Like Tree.toString() but with the positions of the nodes. */
function tree_string(tree: Tree): string {
  let s = "";
  tree.iterate({
    enter(node) {
      s += s === "" || s.endsWith("(") ? "" : ",";
      s += `${node.name}@${node.from.toString()}-${node.to.toString()}(`;
    },
    leave() {
      s = s.endsWith("(") ? s.slice(0, -1) : `${s})`;
    },
  });
  return s;
}

/**
 * Parse the doc, then apply the change and asserts that the resulting
 * (incrementally parsed) tree matches a fresh parse.
 */
function check_incremental_parse(doc: string, change?: ChangeSpec) {
  const language = new Language(defineLanguageFacet(), parser, [], "bc");
  let state = EditorState.create({ doc, extensions: [language] });
  ensureSyntaxTree(state, state.doc.length, 5000);
  if (change) {
    state = state.update({ changes: change }).state;
  }
  const tree = ensureSyntaxTree(state, state.doc.length, 5000);
  ok(tree);
  equal(tree.length, state.doc.length);
  equal(tree_string(tree), tree_string(parser.parse(state.sliceDoc())));
}

const price = "2012-12-12 price USD 1 EUR\n";

/** Deduce the edit for the fragments as [startIndex, oldEndIndex, newEndIndex]. */
function deduce(
  old_length: number,
  input_length: number,
  ...specs: [
    from: number,
    to: number,
    offset: number,
    open_start: boolean,
    open_end: boolean,
  ][]
): [start_index: number, old_end_index: number, new_end_index: number] | null {
  const tree = new Tree(NodeType.none, [], [], old_length);
  const fragments = specs.map(
    ([from, to, offset, open_start, open_end]) =>
      new TreeFragment(from, to, tree, offset, open_start, open_end),
  );
  ok(is_non_empty(fragments));
  const edit = input_edit_for_fragments(fragments, input_length);
  return edit && [edit.startIndex, edit.oldEndIndex, edit.newEndIndex];
}

test("deduce edits from fragments", () => {
  deepEqual(
    deduce(733, 315, [0, 315, 0, false, true]),
    [314, 733, 315],
    "deletion at the end",
  );
  deepEqual(
    deduce(733, 315, [0, 418, 315, true, false]),
    [0, 316, 1],
    "deletion at the start",
  );
  deepEqual(
    deduce(733, 733, [100, 733, 0, true, false]),
    [0, 101, 101],
    "same-length replacement at the start",
  );
  deepEqual(
    deduce(733, 733, [0, 733, 0, false, false]),
    [732, 733, 733],
    "unchanged fragment",
  );
  deepEqual(
    deduce(733, 700, [100, 600, 10, true, true]),
    [0, 733, 700],
    "changes before and after a fragment",
  );
  deepEqual(
    deduce(733, 700, [100, 300, 5, true, true], [400, 600, 10, true, true]),
    [0, 733, 700],
    "changes before, between, and after fragments",
  );
  deepEqual(
    deduce(733, 422, [0, 164, 0, false, true], [164, 422, 311, true, false]),
    [163, 476, 165],
    "deletion in the middle",
  );
  deepEqual(
    deduce(422, 733, [0, 164, 0, false, true], [475, 733, -311, true, false]),
    [163, 165, 476],
    "insertion in the middle",
  );
});

test("parse that reuses a single fragment", () => {
  const tree = parser.parse(price + price);
  equal(tree.length, price.length * 2);
  let fragments = TreeFragment.addTree(tree);
  fragments = TreeFragment.applyChanges(fragments, [
    { fromA: 0, toA: price.length, fromB: 0, toB: 0 },
  ]);
  equal(fragments.length, 1);
  ok(is_non_empty(fragments));
  const edit = input_edit_for_fragments(fragments, price.length);
  equal(edit?.startIndex, 0);
  equal(edit.oldEndIndex, price.length + 1);
  equal(edit.newEndIndex, 1);
  const new_tree = parser.parse(price, fragments);
  equal(tree_string(new_tree), tree_string(parser.parse(price)));
});

test("parse a single price directive", () => {
  equal(
    tree_string(parser.parse(price)),
    "beancount_file@0-27(price@0-27(date@0-10,PRICE@11-16,currency@17-20,amount@21-26(number@21-22,currency@23-26)))",
  );
  ok(parser.startParse(price).advance());
});

test("parse with leading whitespace", () => {
  const doc = `\n  ${price}`;
  const tree = parser.parse(doc);
  equal(tree.length, doc.length);
  equal(
    tree_string(tree),
    "beancount_file@0-30(price@3-30(date@3-13,PRICE@14-19,currency@20-23,amount@24-29(number@24-25,currency@26-29)))",
  );
});

test("parse long documents that are initially only parsed partially", async () => {
  check_incremental_parse(price.repeat(200));
  const long_example = await readFile(
    join(REPOSITORY_ROOT, "tests", "data", "long-example.beancount"),
    "utf8",
  );
  check_incremental_parse(long_example.slice(0, 10000));
});

test("parse incrementally after a same-length replacement", () => {
  const doc = "2012-12-12 *\n  Assets:Cash 10 USD\n  Assets:Bank\n";
  check_incremental_parse(doc, { from: 1, to: 2, insert: "\n" });
  check_incremental_parse(price.repeat(10) + doc, {
    from: price.length * 10 + 1,
    to: price.length * 10 + 2,
    insert: "\n",
  });
});

test("parse incrementally after a change of the containing node", () => {
  const commodity = `1792-01-01 commodity USD
  export: "CASH"
  name: "US Dollar"
  precision: 2
`;
  const doc = price.repeat(10) + commodity + price.repeat(10);
  const from = doc.indexOf(' "CASH"');
  check_incremental_parse(doc, { from, to: from + 9, insert: "10" });
});

test("parse incrementally after changes at the start and end", () => {
  const doc = price.repeat(30);
  const start = { from: 21, insert: " " };
  const end = { from: doc.length - 6, insert: " " };
  check_incremental_parse(doc, [start, end]);
  const middle = { from: price.length * 15 + 21, insert: " " };
  check_incremental_parse(doc, [start, middle, end]);
});

test("parser errors", () => {
  throws(() => new LezerTSParser(new TS.Parser(), [], "beancount_file"));
  throws(() => parser.startParse(price, [], [{ from: 0, to: 1 }]));
});

test("full parses of the same document are cached", () => {
  const doc = Text.of(price.split("\n"));
  const tree = parser.parse(new DocInput(doc));
  const parse = parser.startParse(new DocInput(doc));
  equal(parse.advance(), tree);
  equal(parse.parsedPos, doc.length);
});

test("parse with unusable old trees", async (t) => {
  const log = t.mock.method(console, "error", () => undefined);
  // Use a separate TS parser since its language is unset below.
  const own_ts_parser = await load_beancount_ts_parser();
  const own_parser = new LezerTSParser(own_ts_parser, [], "beancount_file");
  const doc = price.repeat(3);
  const old = own_parser.parse(doc);
  const parse = (fragments: readonly TreeFragment[]) =>
    tree_string(own_parser.parse(doc, fragments));
  const expected = tree_string(old);

  const no_ts_tree = new Tree(NodeType.none, [], [], doc.length);
  equal(parse(TreeFragment.addTree(no_ts_tree)), expected);
  const other = own_parser.parse(price);
  const fragments = [old, other].map(
    (tree, i) => new TreeFragment(i, i + 1, tree, 0),
  );
  equal(parse(fragments), expected, "fragments of different trees");
  const no_children = new Tree(old.type, [], [], doc.length, old.propValues);
  equal(parse(TreeFragment.addTree(no_children)), expected);
  equal(log.mock.callCount(), 2);

  own_ts_parser.setLanguage(null);
  equal(own_parser.startParse(doc).advance(), null, "TS parse fails");
  equal(log.mock.callCount(), 3);
});
