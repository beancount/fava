import { deepEqual, equal, ok } from "node:assert/strict";
import { test } from "node:test";

import { setDiagnosticsEffect } from "@codemirror/lint";
import { EditorState } from "@codemirror/state";

import { align_amounts } from "../src/codemirror/beancount-format.ts";
import {
  replace_contents,
  scroll_to_line,
  set_errors,
} from "../src/codemirror/editor-transactions.ts";
import {
  get_ts_tree,
  LezerTSParser,
} from "../src/codemirror/tree-sitter-parser.ts";
import { load_beancount_ts_parser } from "./helpers.ts";

test("replace editor contents", () => {
  const state = EditorState.create({ doc: "test\n" });
  equal(state.sliceDoc(), "test\n");
  const transaction = state.update(replace_contents(state, "asdfasdf\n"));
  equal(transaction.docChanged, true);
  equal(transaction.state.sliceDoc(), "asdfasdf\n");
});

test("scroll to line", () => {
  const state = EditorState.create({ doc: "test\ntest\ntest\n" });

  const second_line = state.update(scroll_to_line(state, 2));
  equal(second_line.docChanged, false);
  ok(second_line.selection);
  equal(second_line.state.selection.main.from, 5);

  const last_line = state.update(scroll_to_line(state, state.doc.lines));
  equal(last_line.docChanged, false);
  ok(last_line.selection);
  equal(last_line.state.selection.main.from, 15);

  const after_end = state.update(scroll_to_line(state, state.doc.lines + 1));
  equal(after_end.docChanged, false);
  equal(after_end.selection, undefined);

  const line_zero = state.update(scroll_to_line(state, 0));
  equal(line_zero.docChanged, false);
  equal(line_zero.selection, undefined);
});

test("set errors", () => {
  const state = EditorState.create({ doc: "test\ntest\ntest\n" });

  const transaction = state.update(
    set_errors(state, [
      { type: "type", message: "first error", source: null },
      {
        type: "type",
        message: "second error",
        source: { lineno: 100, filename: "asdf" },
      },
      {
        type: "type",
        message: "third error",
        source: { lineno: 2, filename: "asdf" },
      },
    ]),
  );
  const effect = transaction.effects[0];
  ok(effect);
  ok(effect.is(setDiagnosticsEffect));
  deepEqual(effect.value, [
    {
      from: 0,
      to: 4,
      severity: "error",
      message: "first error",
    },
    {
      from: 15,
      to: 15,
      severity: "error",
      message: "second error",
    },
    {
      from: 5,
      to: 9,
      severity: "error",
      message: "third error",
    },
  ]);
});

const parser = new LezerTSParser(
  await load_beancount_ts_parser(),
  [],
  "beancount_file",
);
const changes = (doc: string, column: number) => {
  const tree = get_ts_tree(parser.parse(doc));
  ok(tree);
  return align_amounts(doc, tree, column);
};
const align = (doc: string, column: number): string => {
  const state = EditorState.create({ doc });
  return state.update({ changes: changes(doc, column) }).state.sliceDoc();
};

test("align amounts: the prefix is never truncated", () => {
  equal(
    align("2024-01-02 balance Assets:Cash 10 USD\n", 5),
    "2024-01-02 balance Assets:Cash  10 USD\n",
  );
});

test("align amounts: can handle leading whitespace in the file", () => {
  equal(
    align("\n  2024-01-02 balance Assets:Cash 10 USD\n", 40),
    "\n  2024-01-02 balance Assets:Cash    10 USD\n",
  );
});

test("align amounts: misc examples", () => {
  equal(
    align(
      `2024-01-01 * "Päyee" "10 USD"
  Assets:Cash -10.00   USD {5 EUR} @ 2 EUR ; comment
  ! Assets:Bank (2 + 3) USD
  Assets:Other
    meta: 1 USD
  Assets:Cash 10 @@ 20 EUR
  Assets:Cash 10 USD {{5 EUR}} @@ 20 EUR
2024-01-02 balance Assets:Cash 10 USD
2024-01-02 balance Assets:B 1 ~ 0.1 USD
2024-01-02 price EUR 1.2 USD
`,
      40,
    ),
    `2024-01-01 * "Päyee" "10 USD"
  Assets:Cash                   -10.00 USD {5 EUR} @ 2 EUR ; comment
  ! Assets:Bank                (2 + 3) USD
  Assets:Other
    meta:                            1 USD
  Assets:Cash 10 @@ 20 EUR
  Assets:Cash                       10 USD {{5 EUR}} @@ 20 EUR
2024-01-02 balance Assets:Cash      10 USD
2024-01-02 balance Assets:B    1 ~ 0.1 USD
2024-01-02 price EUR               1.2 USD
`,
  );
});

test("align amounts: the currency is missing (zero-width node inserted by tree-sitter)", () => {
  equal(
    align("2024-01-02 balance Assets:Cash 10\n", 40),
    "2024-01-02 balance Assets:Cash 10\n",
  );
});

test("align amounts: amounts spanning multiple lines are not changed", () => {
  for (const doc of [
    "2024-01-01 balance Assets:A 10\n\n\nUSD\n",
    "2024-01-01 balance Assets:A 10 ; note\n  USD\n",
    "2024-01-01 price USD 10\n; a comment\nEUR\n",
    '2024-01-01 * "Payee"\n  Assets:A (1 +\n   2) USD\n',
  ]) {
    equal(align(doc, 40), doc);
  }
});

test("align amounts: amounts with syntax errors before or in them on their line are not changed", () => {
  for (const doc of [
    "2024-01-01 *\n  Assets:A 1 ~ 2 USD\n",
    "2024-01-01 *\n  Assets:A # 2 USD\n",
    "2024-01-01 *\n  Assets:A (1 # 2) USD\n",
    "2024-01-01 *\n  Assets:A 1 # USD\n",
    "  garbage here 5 EUR\n",
    "2024-01-01 *\n  garbage here 5 EUR\n",
  ]) {
    equal(align(doc, 40), doc);
  }
});

test("align amounts: only the line with the syntax error is left alone", () => {
  equal(
    align(
      `2024-01-01 *
  Assets:A 5 EUR
  garbage
  Assets:B 5 EUR
  Assets:C # 5 EUR
  Assets:D 5 EUR
`,
      40,
    ),
    `2024-01-01 *
  Assets:A                           5 EUR
  garbage
  Assets:B                           5 EUR
  Assets:C # 5 EUR
  Assets:D                           5 EUR
`,
  );
});

test("align amounts: only posting, balance, price, and metadata amounts are aligned", () => {
  for (const doc of [
    '2024-01-01 custom "a" 1 USD 2 EUR\n',
    "pushmeta foo: 1 USD\n",
  ]) {
    equal(align(doc, 40), doc);
  }
});

test("align amounts: no changes if already aligned", () => {
  deepEqual(changes("2024-01-02 price EUR  1.2 USD\n", 27), []);
});
