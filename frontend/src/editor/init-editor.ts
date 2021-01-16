import { basicSetup, EditorState, EditorView } from "@codemirror/basic-setup";
import { defaultHighlightStyle } from "@codemirror/highlight";
import { Prec } from "@codemirror/state";

/**
 * A basic readonly editor.
 */
export function initReadonlyEditor(value: string): EditorView {
  const extensions = [
    basicSetup,
    Prec.fallback(defaultHighlightStyle),
    EditorView.editable.of(false),
  ];
  return new EditorView({
    state: EditorState.create({ doc: value, extensions }),
  });
}
