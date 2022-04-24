import {
  autocompletion,
  closeBrackets,
  closeBracketsKeymap,
  completionKeymap,
} from "@codemirror/autocomplete";
import { defaultKeymap, history, historyKeymap } from "@codemirror/commands";
import {
  bracketMatching,
  defaultHighlightStyle,
  foldGutter,
  foldKeymap,
  indentOnInput,
  indentUnit,
  syntaxHighlighting,
} from "@codemirror/language";
import { lintKeymap } from "@codemirror/lint";
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
  lineNumbers,
  placeholder,
  rectangularSelection,
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
  syntaxHighlighting(defaultHighlightStyle),
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
  return setup(value, [baseExtensions, EditorState.readOnly.of(true)]);
}

/**
 * Read-only editors in the help pages.
 */
export class BeancountTextarea extends HTMLTextAreaElement {
  constructor() {
    super();
    const [view] = setup(this.value, [
      beancount,
      syntaxHighlighting(defaultHighlightStyle),
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
    syntaxHighlighting(defaultHighlightStyle),
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
