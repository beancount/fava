import CodeMirror from 'codemirror';
import URI from 'urijs';
import Mousetrap from 'mousetrap';

import 'codemirror/addon/mode/simple';

// search
import 'codemirror/addon/dialog/dialog';
import 'codemirror/addon/search/searchcursor';
import 'codemirror/addon/search/search';

// print margin
import 'codemirror/addon/display/rulers';

// trailing whitespace
import 'codemirror/addon/edit/trailingspace';

// folding
import 'codemirror/addon/fold/foldcode';
import 'codemirror/addon/fold/foldgutter';

// auto-complete
import 'codemirror/addon/hint/show-hint';

// commenting
import 'codemirror/addon/comment/comment';

// placeholder
import 'codemirror/addon/display/placeholder';

import './codemirror/fold-beancount';
import './codemirror/hint-beancount';
import './codemirror/mode-beancount';

import './codemirror/hint-query';
import './codemirror/mode-query';

import { $, $$, handleJSON } from './helpers';
import e from './events';

CodeMirror.commands.favaSave = (cm) => {
  const button = $('#source-editor-submit');
  const fileName = button.getAttribute('data-filename');

  const buttonText = button.textContent;
  button.disabled = true;
  button.textContent = button.getAttribute('data-progress-content');

  $.fetch(`${window.favaAPI.baseURL}api/source/`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      file_path: fileName,
      source: cm.getValue(),
      sha256sum: $('#source-editor').getAttribute('data-sha256sum'),
    }),
  })
    .then(handleJSON)
    .then((data) => {
      cm.focus();
      $('#source-editor').setAttribute('data-sha256sum', data.sha256sum);
      e.trigger('file-modified');
    }, (error) => {
      e.trigger('error', error);
    })
    .then(() => {
      cm.markClean();
      button.textContent = buttonText;
    });
};

CodeMirror.commands.favaFormat = (cm) => {
  $.fetch(`${window.favaAPI.baseURL}api/format-source/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      source: cm.getValue(),
    }),
  })
    .then(handleJSON)
    .then((data) => {
      const scrollPosition = cm.getScrollInfo().top;
      cm.setValue(data.payload);
      cm.scrollTo(null, scrollPosition);
    }, (error) => {
      e.trigger('error', error);
    });
};

CodeMirror.commands.favaToggleComment = (cm) => {
  const args = { from: cm.getCursor(true), to: cm.getCursor(false), options: { lineComment: ';' } };
  if (!cm.uncomment(args.from, args.to, args.options)) {
    cm.lineComment(args.from, args.to, args.options);
  }
};

CodeMirror.commands.favaCenterCursor = (cm) => {
  const top = cm.cursorCoords(true, 'local').top;
  const height = cm.getScrollInfo().clientHeight;
  cm.scrollTo(null, top - (height / 2));
};

CodeMirror.commands.favaJumpToMarker = (cm) => {
  const cursor = cm.getSearchCursor('FAVA-INSERT-MARKER');

  if (cursor.findNext()) {
    cm.focus();
    cm.setCursor(cursor.pos.from);
    cm.execCommand('goLineUp');
    cm.execCommand('favaCenterCursor');
  } else {
    cm.setCursor(cm.lastLine(), 0);
  }
};

// Initialize the query editor
function initQueryEditor() {
  const queryEditorTextarea = $('#query-editor');
  if (!queryEditorTextarea) { return; }

  const queryOptions = {
    mode: 'beancount-query',
    extraKeys: {
      'Ctrl-Enter': () => {
        $('#submit-query').click();
      },
      'Cmd-Enter': () => {
        $('#submit-query').click();
      },
    },
    placeholder: queryEditorTextarea.getAttribute('placeholder'),
  };
  const editor = CodeMirror.fromTextArea(queryEditorTextarea, queryOptions);

  editor.on('keyup', (cm, event) => {
    if (!cm.state.completionActive && event.keyCode !== 13) {
      CodeMirror.commands.autocomplete(cm, null, { completeSingle: false });
    }
  });

  $.delegate($('#query-container'), 'click', '.queryresults-header', (event) => {
    const wrapper = event.target.closest('.queryresults-wrapper');
    if (wrapper.classList.contains('inactive')) {
      editor.setValue(wrapper.querySelector('code').innerHTML);
      $('#query-form').dispatchEvent(new Event('submit'));
      return;
    }
    wrapper.classList.toggle('toggled');
  });
}

// Initialize read-only editors
export default function initReadOnlyEditors() {
  $$('.editor-readonly').forEach((el) => {
    CodeMirror.fromTextArea(el, {
      mode: 'beancount',
      readOnly: true,
    });
  });
}

e.on('page-loaded', () => {
  initQueryEditor();
  initReadOnlyEditors();

  const sourceEditorTextarea = $('#source-editor');
  if (!sourceEditorTextarea) { return; }

  const rulers = [];
  if (window.favaAPI.favaOptions['editor-print-margin-column']) {
    rulers.push({
      column: window.favaAPI.favaOptions['editor-print-margin-column'],
      lineStyle: 'dotted',
    });
  }

  const options = {
    mode: 'beancount',
    indentUnit: 4,
    lineNumbers: true,
    rulers,
    foldGutter: true,
    showTrailingSpace: true,
    gutters: ['CodeMirror-linenumbers', 'CodeMirror-foldgutter'],
    extraKeys: {
      'Ctrl-Space': 'autocomplete',
      'Ctrl-S': 'favaSave',
      'Cmd-S': 'favaSave',
      'Ctrl-D': 'favaFormat',
      'Cmd-D': 'favaFormat',
      'Ctrl-Y': 'favaToggleComment',
      'Cmd-Y': 'favaToggleComment',
      Tab: (cm) => {
        if (cm.somethingSelected()) {
          cm.indentSelection('add');
        } else {
          cm.execCommand('insertSoftTab');
        }
      },
    },
  };

  const editor = CodeMirror.fromTextArea(sourceEditorTextarea, options);
  const saveButton = $('#source-editor-submit');

  editor.on('changes', (cm) => {
    saveButton.disabled = cm.isClean();
  });

  editor.on('keyup', (cm, event) => {
    if (!cm.state.completionActive && event.keyCode !== 13) {
      CodeMirror.commands.autocomplete(cm, null, { completeSingle: false });
    }
  });
  const line = parseInt(new URI(window.location.search).query(true).line, 10);
  if (line > 0) {
    editor.setCursor(line - 1, 0);
    editor.execCommand('favaCenterCursor');
  } else {
    editor.execCommand('favaJumpToMarker');
  }

  // keybindings when the focus is outside the editor
  Mousetrap.bind(['ctrl+s', 'meta+s'], (event) => {
    event.preventDefault();
    editor.execCommand('favaSave');
  });

  Mousetrap.bind(['ctrl+d', 'meta+d'], (event) => {
    event.preventDefault();
    editor.execCommand('favaFormat');
  });

  // Run editor commands with buttons in editor menu.
  $$('#source-form button').forEach((button) => {
    const command = button.getAttribute('data-command');
    if (command) {
      button.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopImmediatePropagation();
        editor.execCommand(command);
      });
    }
  });
});
