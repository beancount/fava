import { setDiagnosticsEffect } from "@codemirror/lint";
import { EditorState } from "@codemirror/state";
import { test } from "uvu";
import assert from "uvu/assert";

import {
  replaceContents,
  scrollToLine,
  setErrors,
} from "../src/codemirror/editor-transactions";

test("replace editor contents", () => {
  const state = EditorState.create({ doc: "test\n" });
  assert.equal(state.sliceDoc(), "test\n");
  const transaction = state.update(replaceContents(state, "asdfasdf\n"));
  assert.equal(transaction.docChanged, true);
  assert.equal(transaction.state.sliceDoc(), "asdfasdf\n");
});

test("scroll to line", () => {
  const state = EditorState.create({ doc: "test\ntest\ntest\n" });

  const second_line = state.update(scrollToLine(state, 2));
  assert.equal(second_line.docChanged, false);
  assert.ok(second_line.selection);
  assert.equal(second_line.state.selection.main.from, 5);

  const last_line = state.update(scrollToLine(state, state.doc.lines));
  assert.equal(last_line.docChanged, false);
  assert.ok(last_line.selection);
  assert.equal(last_line.state.selection.main.from, 15);

  const after_end = state.update(scrollToLine(state, state.doc.lines + 1));
  assert.equal(after_end.docChanged, false);
  assert.equal(after_end.selection, undefined);

  const line_zero = state.update(scrollToLine(state, 0));
  assert.equal(line_zero.docChanged, false);
  assert.equal(line_zero.selection, undefined);
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
  assert.ok(effect);
  assert.ok(effect.is(setDiagnosticsEffect));
  assert.equal(effect.value, [
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
