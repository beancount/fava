import { deepEqual, equal, ok } from "node:assert/strict";

import { setDiagnosticsEffect } from "@codemirror/lint";
import { EditorState } from "@codemirror/state";
import { test } from "uvu";

import {
  replaceContents,
  scrollToLine,
  setErrors,
} from "../src/codemirror/editor-transactions.ts";

test("replace editor contents", () => {
  const state = EditorState.create({ doc: "test\n" });
  equal(state.sliceDoc(), "test\n");
  const transaction = state.update(replaceContents(state, "asdfasdf\n"));
  equal(transaction.docChanged, true);
  equal(transaction.state.sliceDoc(), "asdfasdf\n");
});

test("scroll to line", () => {
  const state = EditorState.create({ doc: "test\ntest\ntest\n" });

  const second_line = state.update(scrollToLine(state, 2));
  equal(second_line.docChanged, false);
  ok(second_line.selection);
  equal(second_line.state.selection.main.from, 5);

  const last_line = state.update(scrollToLine(state, state.doc.lines));
  equal(last_line.docChanged, false);
  ok(last_line.selection);
  equal(last_line.state.selection.main.from, 15);

  const after_end = state.update(scrollToLine(state, state.doc.lines + 1));
  equal(after_end.docChanged, false);
  equal(after_end.selection, undefined);

  const line_zero = state.update(scrollToLine(state, 0));
  equal(line_zero.docChanged, false);
  equal(line_zero.selection, undefined);
});

test("set errors", () => {
  const state = EditorState.create({ doc: "test\ntest\ntest\n" });

  const transaction = state.update(
    setErrors(state, [
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

test.run();
