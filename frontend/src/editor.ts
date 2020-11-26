import CodeMirror, { Editor } from "codemirror";

import "codemirror/addon/mode/simple";

// search
import "codemirror/addon/dialog/dialog";
import "codemirror/addon/search/searchcursor";
import "codemirror/addon/search/search";

// print margin
import "codemirror/addon/display/rulers";

// trailing whitespace
import "codemirror/addon/edit/trailingspace";

// folding
import "codemirror/addon/fold/foldcode";
import "codemirror/addon/fold/foldgutter";

// auto-complete
import "codemirror/addon/hint/show-hint";

// commenting
import "codemirror/addon/comment/comment";

// placeholder
import "codemirror/addon/display/placeholder";

// highlight line
import "codemirror/addon/selection/active-line";

import "./codemirror/fold-beancount";
import "./codemirror/hint-beancount";
import "./codemirror/mode-beancount";

import "./codemirror/hint-query";
import "./codemirror/mode-query";

import { put } from "./api";
import { notify } from "./notifications";
import { favaAPI } from "./stores";

declare module "codemirror" {
  interface EditorConfiguration {
    // defined in the edit/trailingspace addon
    showTrailingSpace?: boolean;
    // defined in the display/rulers addon
    rulers?: {
      column: number;
      lineStyle: string;
    }[];
  }
  interface CommandActions {
    favaFormat(editor: Editor): void;
    favaToggleComment(editor: Editor): void;
    // defined in the hint/show-hint addon
    autocomplete(
      editor: Editor,
      getHints: undefined,
      options: { completeSingle: boolean }
    ): void;
  }
}

export { CodeMirror };

CodeMirror.commands.favaFormat = (cm: Editor): void => {
  put("format_source", { source: cm.getValue() }).then(
    (data) => {
      const scrollPosition = cm.getScrollInfo().top;
      cm.setValue(data);
      cm.scrollTo(null, scrollPosition);
    },
    (error) => {
      notify(error, "error");
    }
  );
};

CodeMirror.commands.favaToggleComment = (cm: Editor): void => {
  const doc = cm.getDoc();
  const args = {
    from: doc.getCursor("start"),
    to: doc.getCursor("end"),
    options: { lineComment: ";" },
  };
  if (!cm.uncomment(args.from, args.to, args.options)) {
    cm.lineComment(args.from, args.to, args.options);
  }
};

/**
 * Whether the given key should be ignored for autocompletion
 */
function ignoreKey(key: string): boolean {
  switch (key) {
    case "ArrowDown":
    case "ArrowUp":
    case "ArrowLeft":
    case "ArrowRight":
    case "PageDown":
    case "PageUp":
    case "Home":
    case "End":
    case "Escape":
    case "Enter":
    case "Alt":
    case "Control":
    case "Meta":
    case "Shift":
    case "CapsLock":
      return true;
    default:
      return false;
  }
}

export function enableAutomaticCompletions(editor: Editor): void {
  editor.on("keyup", (cm: Editor, event: KeyboardEvent) => {
    if (!cm.state.completionActive && !ignoreKey(event.key)) {
      CodeMirror.commands.autocomplete(cm, undefined, {
        completeSingle: false,
      });
    }
  });
}

/**
 * Scroll to center the cursor in the middle of the editor.
 */
function centerCursor(cm: Editor): void {
  const { top } = cm.cursorCoords(true, "local");
  const height = cm.getScrollInfo().clientHeight;
  cm.scrollTo(null, top - height / 2);
}

/**
 * Jump to the `FAVA-INSERT-MARKER` string.
 */
function jumpToMarker(cm: Editor): void {
  const doc = cm.getDoc();
  const cursor = cm.getSearchCursor("FAVA-INSERT-MARKER");

  if (cursor.findNext()) {
    cm.focus();
    doc.setCursor(cursor.from());
    cm.execCommand("goLineUp");
    centerCursor(cm);
  } else {
    doc.setCursor(doc.lastLine(), 0);
  }
}

/**
 * Read-only editors in the help pages.
 */
export class BeancountTextarea extends HTMLTextAreaElement {
  constructor() {
    super();

    CodeMirror.fromTextArea(this, {
      mode: "beancount",
      readOnly: true,
    });
  }
}

/**
 * Configuration for a source editor.
 * @param save - The function that should be called to save the contents.
 */
export function sourceEditorOptions(
  save: () => void
): CodeMirror.EditorConfiguration {
  const currencyColumn = favaAPI.favaOptions["currency-column"];
  const rulers = currencyColumn
    ? [{ column: currencyColumn - 1, lineStyle: "dotted" }]
    : undefined;
  return {
    mode: "beancount",
    indentUnit: 4,
    lineNumbers: true,
    foldGutter: true,
    showTrailingSpace: true,
    styleActiveLine: true,
    gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
    rulers,
    extraKeys: {
      "Ctrl-Space": "autocomplete",
      "Ctrl-S": save,
      "Cmd-S": save,
      "Ctrl-D": "favaFormat",
      "Cmd-D": "favaFormat",
      "Ctrl-Y": "favaToggleComment",
      "Cmd-Y": "favaToggleComment",
      Tab: (cm: Editor): void => {
        if (cm.getDoc().somethingSelected()) {
          cm.execCommand("indentMore");
        } else {
          cm.execCommand("insertSoftTab");
        }
      },
    },
  };
}

/**
 * Init source editor.
 */
export function initSourceEditor(editor: Editor): void {
  enableAutomaticCompletions(editor);
  const line = parseInt(
    new URLSearchParams(window.location.search).get("line") || "0",
    10
  );
  if (line > 0) {
    editor.getDoc().setCursor(line - 1, 0);
    centerCursor(editor);
  } else {
    jumpToMarker(editor);
  }
}
