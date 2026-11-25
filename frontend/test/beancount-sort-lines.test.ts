import { deepEqual, equal } from "node:assert/strict";
import { test } from "node:test";

import { EditorSelection, EditorState } from "@codemirror/state";

import {
  sort_lines_ascending,
  sort_lines_descending,
} from "../src/codemirror/beancount-sort-lines.ts";

/**
 * Minimal EditorView stand-in: the sort commands only need state + dispatch.
 */
function fake_view(doc: string, from: number, to: number) {
  let state = EditorState.create({
    doc,
    selection: EditorSelection.single(from, to),
  });
  return {
    get state() {
      return state;
    },
    dispatch(tr: Parameters<EditorState["update"]>[0]) {
      state = state.update(tr).state;
    },
  };
}

test("sort lines ascending sorts a selection", () => {
  const doc = "c\nb\na\n";
  const view = fake_view(doc, 0, doc.length);
  equal(sort_lines_ascending(view as never), true);
  deepEqual(view.state.doc.toString(), "a\nb\nc\n");
});

test("sort lines descending reverses lexicographic order", () => {
  const doc = "a\nc\nb";
  const view = fake_view(doc, 0, doc.length);
  equal(sort_lines_descending(view as never), true);
  deepEqual(view.state.doc.toString(), "c\nb\na");
});

test("sort lines with empty selection sorts the whole document", () => {
  const doc =
    "2018-08-04 price VBMPX 63.48 USD\n2014-08-04 price VEA 228.73 USD\n2016-08-04 price ITOT 184.36 USD";
  const view = fake_view(doc, 0, 0);
  equal(sort_lines_ascending(view as never), true);
  deepEqual(
    view.state.doc.toString(),
    "2014-08-04 price VEA 228.73 USD\n2016-08-04 price ITOT 184.36 USD\n2018-08-04 price VBMPX 63.48 USD",
  );
});

test("sort lines is a no-op when already sorted", () => {
  const doc = "a\nb\nc";
  const view = fake_view(doc, 0, doc.length);
  const before = view.state.doc.toString();
  equal(sort_lines_ascending(view as never), true);
  equal(view.state.doc.toString(), before);
});
