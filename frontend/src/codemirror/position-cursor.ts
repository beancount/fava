import { cursorLineUp } from "@codemirror/commands";
import { SearchCursor } from "@codemirror/search";
import { EditorSelection } from "@codemirror/state";
import { EditorView } from "@codemirror/view";

/**
 * Position the cursor
 */
export function positionCursorInSourceEditor(
  cm: EditorView,
  line: number
): void {
  if (line > 0) {
    // Scroll to the given line
    const linePos = cm.state.doc.line(line);
    cm.dispatch({
      selection: { ...linePos, anchor: linePos.from },
      scrollIntoView: true,
    });
  } else {
    // Jump to the `FAVA-INSERT-MARKER` string.
    const cursor = new SearchCursor(cm.state.doc, "FAVA-INSERT-MARKER");
    cursor.next();

    if (cursor.value.from) {
      cm.focus();
      const selection = EditorSelection.cursor(cursor.value.from);
      cm.dispatch({ selection, scrollIntoView: true });
      cursorLineUp(cm);
    } else {
      const selection = EditorSelection.cursor(cm.state.doc.length);
      cm.dispatch({ selection, scrollIntoView: true });
    }
  }
}
