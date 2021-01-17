import { basicSetup, EditorState, EditorView } from "@codemirror/basic-setup";
import { cursorLineUp } from "@codemirror/commands";
import { defaultHighlightStyle } from "@codemirror/highlight";
import { SearchCursor } from "@codemirror/search";
import { EditorSelection, Prec } from "@codemirror/state";
import { KeyBinding, keymap } from "@codemirror/view";

import { beancount } from "../codemirror/beancount";

import { favaKeymap } from "./commands";

/*
 TODO:
 - center cursor?
 - rulers:
const rulers = currencyColumn
    ? [{ column: currencyColumn - 1, lineStyle: "dotted" }]
    : undefined;
*/

/**
 * A basic readonly editor.
 */
export function initReadonlyEditor(value: string): EditorView {
  const extensions = [
    basicSetup,
    Prec.fallback(defaultHighlightStyle),
    EditorView.editable.of(false),
  ];
  return new EditorView({
    state: EditorState.create({ doc: value, extensions }),
  });
}

/**
 * Read-only editors in the help pages.
 */
export class BeancountTextarea extends HTMLTextAreaElement {
  constructor() {
    super();
    const extensions = [
      beancount,
      Prec.fallback(defaultHighlightStyle),
      EditorView.editable.of(false),
    ];
    const view = new EditorView({
      state: EditorState.create({ doc: this.value, extensions }),
    });
    this.parentNode?.insertBefore(view.dom, this);
    this.style.display = "none";
  }
}

/**
 * A Beancount editor.
 */
export function initBeancountEditor(
  value: string,
  onDocChanges: (s: EditorState) => void,
  commands: KeyBinding[]
): EditorView {
  const extensions = [
    basicSetup,
    beancount,
    keymap.of([...favaKeymap, ...commands]),
    EditorView.updateListener.of((update) => {
      if (update.docChanged) {
        onDocChanges(update.state);
      }
    }),
  ];
  return new EditorView({
    state: EditorState.create({ doc: value, extensions }),
  });
}

/**
 * Jump to the `FAVA-INSERT-MARKER` string.
 */
function jumpToMarker(cm: EditorView): void {
  const cursor = new SearchCursor(cm.state.doc, "FAVA-INSERT-MARKER");
  cursor.next();

  if (cursor.value.from) {
    cm.focus();
    const selection = EditorSelection.cursor(cursor.value.from);
    cm.dispatch({ selection, scrollIntoView: true });
    cursorLineUp(cm);
  } else {
    const selection = EditorSelection.cursor(cm.state.doc.length);
    cm.dispatch({ selection, scrollIntoView: true });
  }
}

/**
 * Init source editor.
 */
export function positionCursorInSourceEditor(cm: EditorView): void {
  const line = parseInt(
    new URLSearchParams(window.location.search).get("line") ?? "0",
    10
  );
  if (line > 0) {
    const linePos = cm.state.doc.line(line);
    cm.dispatch({
      selection: { ...linePos, anchor: linePos.from },
      scrollIntoView: true,
    });
  } else {
    jumpToMarker(cm);
  }
}
