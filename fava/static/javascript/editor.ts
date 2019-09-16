import CodeMirror, { Editor, EditorFromTextArea, Position } from "codemirror";
import Mousetrap from "mousetrap";

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

import { select, selectAll, delegate, putAPI } from "./helpers";
import e from "./events";
import router from "./router";
import { notify } from "./notifications";
import { closeOverlay, favaAPI } from "./stores";

interface SearchCursor {
  findNext(): boolean;
  pos: { from: Position; to: Position };
}

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
  interface Editor {
    // defined in the comment/comment addon
    uncomment(
      from: Position,
      to: Position,
      options: { lineComment: string }
    ): boolean;
    // defined in the comment/comment addon
    lineComment(
      from: Position,
      to: Position,
      options: { lineComment: string }
    ): boolean;
    // defined in the comment/comment addon
    getSearchCursor(query: string): SearchCursor;
  }
  interface CommandActions {
    favaSave(editor: EditorFromTextArea): void;
    favaFormat(editor: Editor): void;
    favaToggleComment(editor: Editor): void;
    favaCenterCursor(editor: Editor): void;
    favaJumpToMarker(editor: Editor): void;
    // defined in the hint/show-hint addon
    autocomplete(
      editor: Editor,
      getHints: undefined,
      options: { completeSingle: boolean }
    ): void;
  }
}

// This handles saving in both the main and the overlaid entry editors.
CodeMirror.commands.favaSave = (cm: EditorFromTextArea) => {
  // @ts-ignore
  const button: HTMLButtonElement = cm.getOption("favaSaveButton");

  const buttonText = button.textContent;
  button.disabled = true;
  button.textContent = button.getAttribute("data-progress-content");

  putAPI("source", {
    file_path: button.getAttribute("data-filename"),
    entry_hash: button.getAttribute("data-entry-hash"),
    source: cm.getValue(),
    sha256sum: cm.getTextArea().getAttribute("data-sha256sum"),
  })
    .then(
      data => {
        cm.focus();
        cm.getTextArea().setAttribute("data-sha256sum", data);
        e.trigger("file-modified");
        // Reload the page if an entry was changed.
        if (button.getAttribute("data-entry-hash")) {
          router.reload();
          closeOverlay();
        }
      },
      error => {
        notify(error, "error");
      }
    )
    .then(() => {
      cm.getDoc().markClean();
      button.textContent = buttonText;
    });
};

CodeMirror.commands.favaFormat = (cm: Editor) => {
  putAPI("format_source", { source: cm.getValue() }).then(
    data => {
      const scrollPosition = cm.getScrollInfo().top;
      cm.setValue(data);
      cm.scrollTo(null, scrollPosition);
    },
    error => {
      notify(error, "error");
    }
  );
};

CodeMirror.commands.favaToggleComment = (cm: Editor) => {
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

CodeMirror.commands.favaCenterCursor = (cm: Editor) => {
  const { top } = cm.cursorCoords(true, "local");
  const height = cm.getScrollInfo().clientHeight;
  cm.scrollTo(null, top - height / 2);
};

CodeMirror.commands.favaJumpToMarker = (cm: Editor) => {
  const doc = cm.getDoc();
  const cursor = cm.getSearchCursor("FAVA-INSERT-MARKER");

  if (cursor.findNext()) {
    cm.focus();
    doc.setCursor(cursor.pos.from);
    cm.execCommand("goLineUp");
    cm.execCommand("favaCenterCursor");
  } else {
    doc.setCursor(doc.lastLine(), 0);
  }
};

// If the given key should be ignored for autocompletion
function ignoreKey(key: string) {
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

// Initialize the query editor
function initQueryEditor() {
  const queryForm = select("#query-form") as HTMLFormElement;
  if (!queryForm) {
    return;
  }

  // @ts-ignore
  const queryStringEl: HTMLTextAreaElement = queryForm.elements.query_string;
  const queryOptions = {
    mode: "beancount-query",
    extraKeys: {
      "Ctrl-Enter": (cm: Editor) => {
        (cm as EditorFromTextArea).save();
        e.trigger("form-submit-query", queryForm);
      },
      "Cmd-Enter": (cm: Editor) => {
        (cm as EditorFromTextArea).save();
        e.trigger("form-submit-query", queryForm);
      },
    },
    placeholder: queryStringEl.getAttribute("placeholder") || undefined,
  };
  const editor = CodeMirror.fromTextArea(queryStringEl, queryOptions);

  editor.on("keyup", (cm: Editor, event: Event) => {
    if (
      !cm.state.completionActive &&
      !ignoreKey((event as KeyboardEvent).key)
    ) {
      CodeMirror.commands.autocomplete(cm, undefined, {
        completeSingle: false,
      });
    }
  });

  delegate(
    select("#query-container"),
    "click",
    ".toggle-box-header",
    (event, closest: HTMLDivElement) => {
      const wrapper = closest.closest(".toggle-box");
      if (!wrapper) return;
      if (wrapper.classList.contains("inactive")) {
        const code = wrapper.querySelector("code");
        editor.setValue(code ? code.textContent || "" : "");
        editor.save();
        e.trigger("form-submit-query", queryForm);
        return;
      }
      wrapper.classList.toggle("toggled");
    }
  );
}

// Initialize read-only editors
function initReadOnlyEditors() {
  selectAll("textarea.editor-readonly").forEach(el => {
    CodeMirror.fromTextArea(el as HTMLTextAreaElement, {
      mode: "beancount",
      readOnly: true,
    });
  });
}

const sourceEditorOptions: CodeMirror.EditorConfiguration = {
  mode: "beancount",
  indentUnit: 4,
  lineNumbers: true,
  foldGutter: true,
  showTrailingSpace: true,
  styleActiveLine: true,
  gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
  extraKeys: {
    "Ctrl-Space": "autocomplete",
    "Ctrl-S": "favaSave",
    "Cmd-S": "favaSave",
    "Ctrl-D": "favaFormat",
    "Cmd-D": "favaFormat",
    "Ctrl-Y": "favaToggleComment",
    "Cmd-Y": "favaToggleComment",
    Tab: (cm: Editor) => {
      if (cm.getDoc().somethingSelected()) {
        cm.execCommand("indentMore");
      } else {
        cm.execCommand("insertSoftTab");
      }
    },
  },
};

let activeEditor: Editor | null = null;
// Init source editor.
export default function initSourceEditor(name: string) {
  if (favaAPI.favaOptions["currency-column"]) {
    sourceEditorOptions.rulers = [
      {
        column: favaAPI.favaOptions["currency-column"] - 1,
        lineStyle: "dotted",
      },
    ];
  }

  const sourceEditorTextarea = select(name) as HTMLTextAreaElement;
  if (!sourceEditorTextarea) {
    return;
  }

  const editor = CodeMirror.fromTextArea(
    sourceEditorTextarea,
    sourceEditorOptions
  );
  if (name === "#source-editor") {
    activeEditor = editor;
  }
  const saveButton = select(`${name}-submit`) as HTMLButtonElement;
  // @ts-ignore
  editor.setOption("favaSaveButton", saveButton);

  editor.on("changes", (cm: Editor) => {
    saveButton.disabled = cm.getDoc().isClean();
  });

  editor.on("keyup", (cm: Editor, event: Event) => {
    if (
      !cm.state.completionActive &&
      !ignoreKey((event as KeyboardEvent).key)
    ) {
      CodeMirror.commands.autocomplete(cm, undefined, {
        completeSingle: false,
      });
    }
  });
  const line = parseInt(
    new URLSearchParams(window.location.search).get("line") || "0",
    10
  );
  if (line > 0) {
    editor.getDoc().setCursor(line - 1, 0);
    editor.execCommand("favaCenterCursor");
  } else {
    editor.execCommand("favaJumpToMarker");
  }

  // keybindings when the focus is outside the editor
  Mousetrap.bind(["ctrl+s", "meta+s"], event => {
    event.preventDefault();
    editor.execCommand("favaSave");
  });

  Mousetrap.bind(["ctrl+d", "meta+d"], event => {
    event.preventDefault();
    editor.execCommand("favaFormat");
  });

  // Run editor commands with buttons in editor menu.
  selectAll(`${name}-form button`).forEach(button => {
    const command = button.getAttribute("data-command");
    if (command) {
      button.addEventListener("click", event => {
        event.preventDefault();
        event.stopImmediatePropagation();
        editor.execCommand(command);
      });
    }
  });
}

e.on("page-loaded", () => {
  initQueryEditor();
  initReadOnlyEditors();
  initSourceEditor("#source-editor");
});

const leaveMessage =
  "There are unsaved changes. Are you sure you want to leave?";

e.on("navigate", (state: { interrupt?: boolean }) => {
  if (activeEditor) {
    if (!activeEditor.getDoc().isClean()) {
      const leave = window.confirm(leaveMessage); // eslint-disable-line no-alert
      if (!leave) {
        state.interrupt = true;
      } else {
        activeEditor = null;
      }
    } else {
      activeEditor = null;
    }
  }
});

window.addEventListener("beforeunload", event => {
  if (activeEditor && !activeEditor.getDoc().isClean()) {
    event.returnValue = leaveMessage;
  }
});
