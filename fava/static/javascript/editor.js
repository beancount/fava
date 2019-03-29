import CodeMirror from "codemirror";
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

import { $, $$, delegate, fetch, handleJSON } from "./helpers";
import e from "./events";
import { notify } from "./notifications";
import { closeOverlay } from "./stores";

// This handles saving in both the main and the overlaid entry editors.
CodeMirror.commands.favaSave = cm => {
  const button = cm.getOption("favaSaveButton");

  const buttonText = button.textContent;
  button.disabled = true;
  button.textContent = button.getAttribute("data-progress-content");

  fetch(`${window.favaAPI.baseURL}api/source/`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      file_path: button.getAttribute("data-filename"),
      entry_hash: button.getAttribute("data-entry-hash"),
      source: cm.getValue(),
      sha256sum: cm.getTextArea().getAttribute("data-sha256sum"),
    }),
  })
    .then(handleJSON)
    .then(
      data => {
        cm.focus();
        cm.getTextArea().setAttribute("data-sha256sum", data.sha256sum);
        e.trigger("file-modified");
        // Reload the page if an entry was changed.
        if (button.getAttribute("data-entry-hash")) {
          e.trigger("reload");
          closeOverlay();
        }
      },
      error => {
        notify(error, "error");
      }
    )
    .then(() => {
      cm.markClean();
      button.textContent = buttonText;
    });
};

CodeMirror.commands.favaFormat = cm => {
  fetch(`${window.favaAPI.baseURL}api/format-source/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      source: cm.getValue(),
    }),
  })
    .then(handleJSON)
    .then(
      data => {
        const scrollPosition = cm.getScrollInfo().top;
        cm.setValue(data.payload);
        cm.scrollTo(null, scrollPosition);
      },
      error => {
        notify(error, "error");
      }
    );
};

CodeMirror.commands.favaToggleComment = cm => {
  const args = {
    from: cm.getCursor(true),
    to: cm.getCursor(false),
    options: { lineComment: ";" },
  };
  if (!cm.uncomment(args.from, args.to, args.options)) {
    cm.lineComment(args.from, args.to, args.options);
  }
};

CodeMirror.commands.favaCenterCursor = cm => {
  const { top } = cm.cursorCoords(true, "local");
  const height = cm.getScrollInfo().clientHeight;
  cm.scrollTo(null, top - height / 2);
};

CodeMirror.commands.favaJumpToMarker = cm => {
  const cursor = cm.getSearchCursor("FAVA-INSERT-MARKER");

  if (cursor.findNext()) {
    cm.focus();
    cm.setCursor(cursor.pos.from);
    cm.execCommand("goLineUp");
    cm.execCommand("favaCenterCursor");
  } else {
    cm.setCursor(cm.lastLine(), 0);
  }
};

// If the given key should be ignored for autocompletion
function ignoreKey(key) {
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
  const queryForm = $("#query-form");
  if (!queryForm) {
    return;
  }

  const queryOptions = {
    mode: "beancount-query",
    extraKeys: {
      "Ctrl-Enter": cm => {
        cm.save();
        e.trigger("form-submit-query", queryForm);
      },
      "Cmd-Enter": cm => {
        cm.save();
        e.trigger("form-submit-query", queryForm);
      },
    },
    placeholder: queryForm.elements.query_string.getAttribute("placeholder"),
  };
  const editor = CodeMirror.fromTextArea(
    queryForm.elements.query_string,
    queryOptions
  );

  editor.on("keyup", (cm, event) => {
    if (!cm.state.completionActive && !ignoreKey(event.key)) {
      CodeMirror.commands.autocomplete(cm, null, { completeSingle: false });
    }
  });

  delegate($("#query-container"), "click", ".toggle-box-header", event => {
    const wrapper = event.target.closest(".toggle-box");
    if (wrapper.classList.contains("inactive")) {
      editor.setValue(wrapper.querySelector("code").textContent);
      editor.save();
      e.trigger("form-submit-query", queryForm);
      return;
    }
    wrapper.classList.toggle("toggled");
  });
}

// Initialize read-only editors
function initReadOnlyEditors() {
  $$(".editor-readonly").forEach(el => {
    CodeMirror.fromTextArea(el, {
      mode: "beancount",
      readOnly: true,
    });
  });
}

const sourceEditorOptions = {
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
    Tab: cm => {
      if (cm.somethingSelected()) {
        cm.indentSelection("add");
      } else {
        cm.execCommand("insertSoftTab");
      }
    },
  },
};

let activeEditor = null;
// Init source editor.
export default function initSourceEditor(name) {
  sourceEditorOptions.rulers = [];
  if (window.favaAPI.favaOptions["currency-column"]) {
    sourceEditorOptions.rulers.push({
      column: window.favaAPI.favaOptions["currency-column"] - 1,
      lineStyle: "dotted",
    });
  }

  const sourceEditorTextarea = $(name);
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
  const saveButton = $(`${name}-submit`);
  editor.setOption("favaSaveButton", saveButton);

  editor.on("changes", cm => {
    saveButton.disabled = cm.isClean();
  });

  editor.on("keyup", (cm, event) => {
    if (!cm.state.completionActive && !ignoreKey(event.key)) {
      CodeMirror.commands.autocomplete(cm, null, { completeSingle: false });
    }
  });
  const line = parseInt(
    new URLSearchParams(window.location.search).get("line"),
    10
  );
  if (line > 0) {
    editor.setCursor(line - 1, 0);
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
  $$(`${name}-form button`).forEach(button => {
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

e.on("navigate", state => {
  if (activeEditor) {
    if (!activeEditor.isClean()) {
      const leave = window.confirm(leaveMessage); // eslint-disable-line no-alert
      if (!leave) {
        state.interrupt = true; // eslint-disable-line no-param-reassign
      } else {
        activeEditor = null;
      }
    } else {
      activeEditor = null;
    }
  }
});

window.addEventListener("beforeunload", event => {
  if (activeEditor && !activeEditor.isClean()) {
    event.returnValue = leaveMessage; // eslint-disable-line no-param-reassign
  }
});
