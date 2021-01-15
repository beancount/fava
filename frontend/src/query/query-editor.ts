import { basicSetup, EditorState, EditorView } from "@codemirror/basic-setup";
import { keymap, placeholder } from "@codemirror/view";

import { bql } from "../codemirror/bql";
import { _ } from "../i18n";

export function initQueryEditor(
  value: string | undefined,
  onChanges: (s: string) => void,
  submit: () => void
): EditorView {
  const extensions = [
    basicSetup,
    bql,
    EditorView.updateListener.of((update) => {
      if (update.docChanged) {
        onChanges(update.state.doc.toString());
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
    placeholder(_("...enter a BQL query. 'help' to list available commands.")),
  ];

  return new EditorView({
    state: EditorState.create({ doc: value, extensions }),
  });
}
