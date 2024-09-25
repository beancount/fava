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
import type { LanguageSupport } from "@codemirror/language";
import {
  bracketMatching,
  defaultHighlightStyle,
  foldGutter,
  foldKeymap,
  indentOnInput,
  indentUnit,
  syntaxHighlighting,
} from "@codemirror/language";
import { lintGutter, lintKeymap } from "@codemirror/lint";
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
import type { Action } from "svelte/action";
import { get as store_get } from "svelte/store";

import { log_error } from "../log";
import { fava_options } from "../stores";
import { getBeancountLanguageSupport } from "./beancount";
import {
  beancountEditorHighlight,
  beancountQueryHighlight,
} from "./beancount-highlight";
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
interface EditorAndAction {
  editor: EditorView;
  renderEditor: Action<HTMLDivElement | HTMLPreElement>;
}

function setup(
  value: string | undefined,
  extensions: Extension[],
): EditorAndAction {
  const view = new EditorView({
    state: EditorState.create({ doc: value, extensions }),
  });
  return {
    editor: view,
    renderEditor: (el) => {
      el.appendChild(view.dom);
    },
  };
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
    getBeancountLanguageSupport()
      .then((beancount) => {
        const { editor } = setup(this.value, [
          beancount,
          syntaxHighlighting(defaultHighlightStyle),
          EditorView.editable.of(false),
        ]);
        this.parentNode?.insertBefore(editor.dom, this);
        this.style.display = "none";
      })
      .catch(log_error);
  }
}

/**
 * A Beancount editor.
 */
export function initBeancountEditor(
  value: string,
  onDocChanges: (s: EditorState) => void,
  commands: KeyBinding[],
  beancount: LanguageSupport,
): EditorAndAction {
  const { indent, currency_column } = store_get(fava_options);
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
    syntaxHighlighting(beancountEditorHighlight),
  ]);
}

/**
 * A basic readonly BQL editor that only does syntax highlighting.
 */
export function initReadonlyQueryEditor(value: string): EditorAndAction {
  return setup(value, [
    bql,
    syntaxHighlighting(beancountQueryHighlight),
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
  submit: () => void,
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
    syntaxHighlighting(beancountQueryHighlight),
  ]);
}
