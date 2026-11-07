import type { EditorView } from "@codemirror/view";
import type { Attachment } from "svelte/attachments";

import { log_error } from "../log.ts";

/**
 * Read-only editors in the help pages.
 *
 * This lazily imports ./beancount.ts to only pull in codemirror
 * and the Beancount parser when used.
 */
export class BeancountCode extends HTMLElement {
  constructor() {
    super();
    import("./beancount.ts")
      .then(({ init_readonly_editor }) => {
        init_readonly_editor(this);
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
