import { syntaxHighlighting } from "@codemirror/language";
import { EditorState } from "@codemirror/state";
import { EditorView, keymap, placeholder } from "@codemirror/view";

import { base_extensions } from "./base-extensions.ts";
import { bql_highlight } from "./bql-highlight.ts";
import { bql_language_support } from "./bql-language.ts";

export { replace_contents } from "./editor-transactions.ts";

/**
 * A basic readonly editor for an asynchronously loaded document.
 *
 * This doesn't use any of the BQL syntax but is provided in this file
 * to avoid more smaller chunks.
 */
export function init_document_preview_editor(): EditorView {
  return new EditorView({
    extensions: [
      base_extensions,
      EditorState.readOnly.of(true),
      placeholder("Loading..."),
    ],
  });
}

/**
 * A basic readonly BQL editor that only does syntax highlighting.
 */
export function init_readonly_query_editor(value: string): EditorView {
  return new EditorView({
    doc: value,
    extensions: [
      bql_language_support,
      syntaxHighlighting(bql_highlight),
      EditorState.readOnly.of(true),
    ],
  });
}

/**
 * The main BQL editor.
 */
export function init_query_editor(
  value: string,
  onDocChanges: (s: EditorState) => void,
  placeholder_value: string,
  get_submit: () => () => void,
): EditorView {
  return new EditorView({
    doc: value,
    extensions: [
      bql_language_support,
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
            const submit = get_submit();
            submit();
            return true;
          },
        },
      ]),
      placeholder(placeholder_value),
      base_extensions,
      syntaxHighlighting(bql_highlight),
    ],
  });
}
