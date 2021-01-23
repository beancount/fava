import { indentSelection } from "@codemirror/commands";
import { EditorSelection } from "@codemirror/state";
import { Command } from "@codemirror/view";

export const tabCommand: Command = (cm) => {
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
