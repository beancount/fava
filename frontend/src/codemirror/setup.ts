import { autocompletion, completionKeymap } from "@codemirror/autocomplete";
import { closeBrackets, closeBracketsKeymap } from "@codemirror/closebrackets";
import { defaultKeymap } from "@codemirror/commands";
import { commentKeymap } from "@codemirror/comment";
import { foldGutter, foldKeymap } from "@codemirror/fold";
import { lineNumbers } from "@codemirror/gutter";
import { defaultHighlightStyle } from "@codemirror/highlight";
import { history, historyKeymap } from "@codemirror/history";
import { indentOnInput, indentUnit } from "@codemirror/language";
import { lintKeymap } from "@codemirror/lint";
import { bracketMatching } from "@codemirror/matchbrackets";
import { rectangularSelection } from "@codemirror/rectangular-selection";
import { highlightSelectionMatches, searchKeymap } from "@codemirror/search";
import type { Extension } from "@codemirror/state";
import { EditorState } from "@codemirror/state";
import type { KeyBinding } from "@codemirror/view";
import {
  drawSelection,
  EditorView,
  highlightActiveLine,
  highlightSpecialChars,
  keymap,
  placeholder,
} from "@codemirror/view";
import { get } from "svelte/store";

import { favaOptions } from "../stores";

import { beancount } from "./beancount";
import { bql } from "./bql";

const baseExtensions = [
  lineNumbers(),
  highlightSpecialChars(),
  history(),
  foldGutter(),
  drawSelection(),
  EditorState.allowMultipleSelections.of(true),
  indentOnInput(),
  defaultHighlightStyle,
  bracketMatching(),
  closeBrackets(),
  autocompletion(),
  rectangularSelection(),
  highlightActiveLine(),
  highlightSelectionMatches(),
  keymap.of([
    ...closeBracketsKeymap,
    ...defaultKeymap,
    ...searchKeymap,
    ...historyKeymap,
    ...foldKeymap,
    ...commentKeymap,
    ...completionKeymap,
    ...lintKeymap,
  ]),
];

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
  return setup(value, [baseExtensions, EditorView.editable.of(false)]);
}

/**
 * Read-only editors in the help pages.
 */
export class BeancountTextarea extends HTMLTextAreaElement {
  constructor() {
    super();
    const [view] = setup(this.value, [
      beancount,
      defaultHighlightStyle,
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
    beancount,
    indentUnit.of(" ".repeat(get(favaOptions).indent)),
    keymap.of(commands),
    EditorView.updateListener.of((update) => {
      if (update.docChanged) {
        onDocChanges(update.state);
      }
    }),
    baseExtensions,
  ]);
}

/**
 * A basic readonly BQL editor that only does syntax highlighting.
 */
export function initReadonlyQueryEditor(value: string): EditorAndAction {
  return setup(value, [
    bql,
    defaultHighlightStyle,
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
    baseExtensions,
  ]);
}
