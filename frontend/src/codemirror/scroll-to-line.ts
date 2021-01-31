import { EditorView } from "@codemirror/view";

/**
 * Select the line with the given number and scroll it into view.
 */
export function scrollToLine(cm: EditorView, line: number): void {
  const linePos = cm.state.doc.line(line);
  cm.dispatch({
    selection: { ...linePos, anchor: linePos.from },
    scrollIntoView: true,
  });
}
