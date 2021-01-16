import { indentSelection } from "@codemirror/commands";
import { EditorSelection } from "@codemirror/state";
import { Command, KeyBinding } from "@codemirror/view";

import { put } from "../api";
import { notify } from "../notifications";

export const favaFormat: Command = (cm) => {
  put("format_source", { source: cm.state.doc.toString() }).then(
    (data) => {
      cm.dispatch({
        changes: { from: 0, to: cm.state.doc.length, insert: data },
      });
    },
    (error) => {
      notify(error, "error");
    }
  );
  return true;
};

const tabCommand: Command = (cm) => {
  const { selection, tabSize } = cm.state;
  if (selection.ranges.length === 1 && selection.main.empty) {
    cm.dispatch({
      changes: {
        from: selection.main.from,
        insert: " ".repeat(tabSize),
      },
      selection: EditorSelection.single(selection.main.from + tabSize),
    });
  } else {
    indentSelection(cm);
  }
  return true;
};

export const favaKeymap: KeyBinding[] = [
  { key: "Control-d", mac: "Meta-d", run: favaFormat },
  { key: "Tab", run: tabCommand },
];
