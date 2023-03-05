import {
  autocompletion,
  closeBrackets,
  closeBracketsKeymap,
  completionKeymap,
} from "@codemirror/autocomplete";
import {
  defaultKeymap,
  history,
  historyKeymap,
  indentWithTab,
} from "@codemirror/commands";
import {
  bracketMatching,
  defaultHighlightStyle,
  foldGutter,
  foldKeymap,
  indentOnInput,
  indentUnit,
  syntaxHighlighting,
} from "@codemirror/language";
import { lintGutter, lintKeymap, setDiagnostics } from "@codemirror/lint";
import type { Diagnostic } from "@codemirror/lint";
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

import type { BeancountError } from "../api/validators";
import { fava_options } from "../stores";

import { beancount } from "./beancount";
import { bql } from "./bql";
import { rulerPlugin } from "./ruler";

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
  lintGutter(),
  keymap.of([
    ...closeBracketsKeymap,
    ...defaultKeymap,
    ...searchKeymap,
    ...historyKeymap,
    ...foldKeymap,
    ...completionKeymap,
    ...lintKeymap,
    indentWithTab,
  ]),
];

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
 * A basic readonly editor for an asynchronously loaded document.
 */
export function initDocumentPreviewEditor(value: string): EditorAndAction {
  return setup(value, [
    baseExtensions,
    EditorState.readOnly.of(true),
    placeholder("Loading..."),
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
  const { indent, currency_column } = get(fava_options);
  return setup(value, [
    beancount,
    indentUnit.of(" ".repeat(indent)),
    ...(currency_column ? [rulerPlugin(currency_column - 1)] : []),
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
 * Set errors for in the editor, highlighting them
 */
export function setErrors(editor: EditorView, errors: BeancountError[]) {
  const diagnostics = errors.map((error): Diagnostic => {
    // Show errors without an attached line on first line
    const line = editor.state.doc.line(error.source?.lineno ?? 1);
    return {
      from: line.from,
      to: line.to,
      severity: "error",
      message: error.message,
    };
  });
  editor.dispatch(setDiagnostics(editor.state, diagnostics));
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
