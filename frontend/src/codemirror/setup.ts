import { basicSetup, EditorState, EditorView } from "@codemirror/basic-setup";
import { cursorLineUp } from "@codemirror/commands";
import { defaultHighlightStyle } from "@codemirror/highlight";
import { SearchCursor } from "@codemirror/search";
import { EditorSelection, Extension, Prec } from "@codemirror/state";
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

/** An editor and a function to attach it to a DOM element. */
type EditorAndAction = [EditorView, (el: HTMLElement) => void];

function setup(
  value: string | undefined,
  extensions: Extension[]
): EditorAndAction {
  const view = new EditorView({
    state: EditorState.create({ doc: value, extensions }),
  });
  return [view, (el) => el.appendChild(view.dom)];
}

/**
 * A basic readonly editor.
 */
export function initReadonlyEditor(value: string): EditorAndAction {
  return setup(value, [
    basicSetup,
    Prec.fallback(defaultHighlightStyle),
    EditorView.editable.of(false),
  ]);
}

/**
 * Read-only editors in the help pages.
 */
export class BeancountTextarea extends HTMLTextAreaElement {
  constructor() {
    super();
    const [view] = setup(this.value, [
      beancount,
      Prec.fallback(defaultHighlightStyle),
      EditorView.editable.of(false),
    ]);
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
): EditorAndAction {
  return setup(value, [
    basicSetup,
    beancount,
    keymap.of([...favaKeymap, ...commands]),
    EditorView.updateListener.of((update) => {
      if (update.docChanged) {
        onDocChanges(update.state);
      }
    }),
  ]);
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
export function initReadonlyQueryEditor(value: string): EditorAndAction {
  return setup(value, [
    bql,
    Prec.fallback(defaultHighlightStyle),
    EditorView.editable.of(false),
  ]);
}

/**
 * The main BQL editor.
 */
export function initQueryEditor(
  value: string | undefined,
  onDocChanges: (s: EditorState) => void,
  _placeholder: string,
  submit: () => void
): EditorAndAction {
  return setup(value, [
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
  ]);
}
