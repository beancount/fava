import type { EditorView } from "@codemirror/view";
import type { Attachment } from "svelte/attachments";

import { log_error } from "../log.ts";

/**
 * Read-only editors in the help pages.
 *
 * This lazily imports ./setup.ts to only pull in codemirror
 * and the Beancount parser when used.
 */
export class BeancountTextarea extends HTMLTextAreaElement {
  constructor() {
    super();
    import("./beancount.ts")
      .then(({ init_textarea }) => {
        init_textarea(this);
      })
      .catch(log_error);
  }
}

/**
 * A Svelte attachment to add an editor to a DOM element.
 */
export function attach_editor(
  editor: EditorView,
): Attachment<HTMLDivElement | HTMLPreElement> {
  return (el) => {
    el.appendChild(editor.dom);

    return () => {
      el.removeChild(editor.dom);
    };
  };
}
