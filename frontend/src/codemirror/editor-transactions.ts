/**
 * All changes to a CodeMirror editor happen as transactions that can be dispatched on the editor.
 */

import type { Diagnostic } from "@codemirror/lint";
import { setDiagnostics } from "@codemirror/lint";
import type { EditorState, TransactionSpec } from "@codemirror/state";

import type { BeancountError } from "../api/validators";

/**
 * Returns a transaction to completely replace the contents of the editor with the given value.
 */
export function replaceContents(
  state: EditorState,
  value: string,
): TransactionSpec {
  return {
    changes: { from: 0, to: state.doc.length, insert: value },
  };
}

/**
 * Returns a transaction to select the line with the given number and scroll it into view.
 */
export function scrollToLine(
  state: EditorState,
  line: number,
): TransactionSpec {
  if (line < 1 || line > state.doc.lines) {
    return {};
  }
  const linePos = state.doc.line(line);
  return {
    selection: { ...linePos, anchor: linePos.from },
    scrollIntoView: true,
  };
}

/**
 * Returns a transaction that set diagnostics for Beancount errors for in the editor, highlighting them.
 */
export function setErrors(
  state: EditorState,
  errors: BeancountError[],
): TransactionSpec {
  const { doc } = state;
  const diagnostics = errors.map(({ source, message }): Diagnostic => {
    // Show errors without a line number on first line and ensure it is within the document.
    const lineno = Math.min(Math.max(source?.lineno ?? 1, 1), doc.lines);
    const line = doc.line(lineno);
    return {
      from: line.from,
      to: line.to,
      severity: "error",
      message,
    };
  });
  return setDiagnostics(state, diagnostics);
}
