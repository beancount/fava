import { deepEqual, equal, ok } from "node:assert/strict";
import { test } from "node:test";

import { setDiagnosticsEffect } from "@codemirror/lint";
import { EditorState } from "@codemirror/state";

import {
  replace_contents,
  scroll_to_line,
  set_errors,
} from "../src/codemirror/editor-transactions.ts";

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
