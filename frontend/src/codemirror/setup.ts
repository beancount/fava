import { basicSetup, EditorState, EditorView } from "@codemirror/basic-setup";
import { cursorLineUp } from "@codemirror/commands";
import { defaultHighlightStyle } from "@codemirror/highlight";
import { SearchCursor } from "@codemirror/search";
import { EditorSelection, Prec } from "@codemirror/state";
import { KeyBinding, keymap, placeholder } from "@codemirror/view";

import { beancount } from "./beancount";
import { bql } from "./bql";
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
 * Position the cursor
 */
export function positionCursorInSourceEditor(
  cm: EditorView,
  line: number
): void {
  if (line > 0) {
    // Scroll to the given line
    const linePos = cm.state.doc.line(line);
    cm.dispatch({
      selection: { ...linePos, anchor: linePos.from },
      scrollIntoView: true,
    });
  } else {
    // Jump to the `FAVA-INSERT-MARKER` string.
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
}

/**
 * A basic readonly BQL editor that only does syntax highlighting.
 */
export function initReadonlyQueryEditor(value: string): EditorView {
  const extensions = [
    bql,
    Prec.fallback(defaultHighlightStyle),
    EditorView.editable.of(false),
  ];
  return new EditorView({
    state: EditorState.create({ doc: value, extensions }),
  });
}

/**
 * The main BQL editor.
 */
export function initQueryEditor(
  value: string | undefined,
  onDocChanges: (s: EditorState) => void,
  _placeholder: string,
  submit: () => void
): EditorView {
  const extensions = [
    basicSetup,
    bql,
    EditorView.updateListener.of((update) => {
      if (update.docChanged) {
        onDocChanges(update.state);
      }
    }),
    keymap.of([
      {
        key: "Control-Enter",
        mac: "Meta-Enter",
        run: () => {
          submit();
          return true;
        },
      },
    ]),
    placeholder(_placeholder),
  ];

  return new EditorView({
    state: EditorState.create({ doc: value, extensions }),
  });
}
