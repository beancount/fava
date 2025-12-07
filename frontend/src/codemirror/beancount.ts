import {
  defaultHighlightStyle,
  indentUnit,
  syntaxHighlighting,
} from "@codemirror/language";
import { EditorState } from "@codemirror/state";
import type { KeyBinding } from "@codemirror/view";
import { EditorView, keymap } from "@codemirror/view";

import { base_extensions } from "./base-extensions.ts";
import { beancount_highlight } from "./beancount-highlight.ts";
import { beancount_language_support } from "./beancount-language.ts";
import { ruler_plugin } from "./ruler.ts";

export { beancount_format } from "./beancount-format.ts";
export {
  replace_contents,
  scroll_to_line,
  set_errors,
} from "./editor-transactions.ts";
export { toggleComment } from "@codemirror/commands";
export { foldAll, unfoldAll } from "@codemirror/language";

export function init_textarea(el: HTMLTextAreaElement): void {
  const editor = new EditorView({
    doc: el.value,
    extensions: [
      beancount_language_support,
      syntaxHighlighting(defaultHighlightStyle),
      EditorState.readOnly.of(true),
    ],
  });
  el.parentNode?.insertBefore(editor.dom, el);
  el.style.display = "none";
}

/**
 * A Beancount editor.
 */
export function init_beancount_editor(
  value: string,
  onDocChanges: (s: EditorState) => void,
  commands: KeyBinding[],
  $indent: number,
  $currency_column: number,
): EditorView {
  return new EditorView({
    doc: value,
    extensions: [
      beancount_language_support,
      indentUnit.of(" ".repeat($indent)),
      ...($currency_column ? [ruler_plugin($currency_column - 1)] : []),
      keymap.of(commands),
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          onDocChanges(update.state);
        }
      }),
      base_extensions,
      syntaxHighlighting(beancount_highlight),
    ],
  });
}
