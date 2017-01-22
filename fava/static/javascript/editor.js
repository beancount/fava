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

import './codemirror/fold-beancount';
import './codemirror/hint-beancount';
import './codemirror/mode-beancount';

import './codemirror/hint-query';
import './codemirror/mode-query';

import { $, $$, _, handleJSON } from './helpers';
import e from './events';

function saveEditorContent(cm) {
  const button = $('#source-editor-submit');
  const fileName = $('#source-editor-select').value;
  const url = button.getAttribute('data-url');

  button.disabled = true;
  button.textContent = _('Saving...');

  $.fetch(url, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      file_path: fileName,
      source: cm.getValue(),
    }),
  })
    .then(handleJSON)
    .then(() => {
      cm.focus();
      e.trigger('file-modified');
    }, () => {
      e.trigger('error', _('Saving ${fileName} failed.', { fileName }));  // eslint-disable-line no-template-curly-in-string
    })
    .then(() => {
      cm.markClean();
      button.textContent = _('Save');
    });
}

function formatEditorContent(cm) {
  const button = $('#source-editor-format');
  const scrollPosition = cm.getScrollInfo().top;
  button.disabled = true;

  $.fetch(button.getAttribute('data-url'), {
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
      cm.setValue(data.payload);
      cm.scrollTo(null, scrollPosition);
    }, () => {
      e.trigger('error', _('Formatting the file with bean-format failed.'));
    })
    .then(() => {
      button.disabled = false;
    });
}

function toggleComment(cm) {
  const args = { from: cm.getCursor(true), to: cm.getCursor(false), options: { lineComment: ';' } };
  if (!cm.uncomment(args.from, args.to, args.options)) {
    cm.lineComment(args.from, args.to, args.options);
  }
}

function centerCursor(cm) {
  const top = cm.cursorCoords(true, 'local').top;
  const height = cm.getScrollInfo().clientHeight;
  cm.scrollTo(null, top - (height / 2));
}

function jumpToMarker(cm) {
  const cursor = cm.getSearchCursor('FAVA-INSERT-MARKER');

  if (cursor.findNext()) {
    cm.focus();
    cm.setCursor(cursor.pos.from);
    cm.execCommand('goLineUp');
    centerCursor(cm);
  } else {
    cm.setCursor(cm.lastLine(), 0);
  }
}

function submitQuery() {
  $('#submit-query').click();
}

export default function initEditor() {
  const rulers = [];
  if (window.favaAPI['editor-print-margin-column']) {
    rulers.push({
      column: window.favaAPI['editor-print-margin-column'],
      lineStyle: 'dotted',
    });
  }

  const defaultOptions = {
    mode: 'beancount',
    indentUnit: 4,
    lineNumbers: true,
    rulers,
    foldGutter: true,
    showTrailingSpace: true,
    gutters: ['CodeMirror-linenumbers', 'CodeMirror-foldgutter'],
    extraKeys: {
      'Ctrl-Space': 'autocomplete',
      'Ctrl-S': (cm) => {
        saveEditorContent(cm);
      },
      'Cmd-S': (cm) => {
        saveEditorContent(cm);
      },
      'Ctrl-D': (cm) => {
        formatEditorContent(cm);
      },
      'Cmd-D': (cm) => {
        formatEditorContent(cm);
      },
      'Ctrl-Y': (cm) => {
        toggleComment(cm);
      },
      'Cmd-Y': (cm) => {
        toggleComment(cm);
      },
      Tab: (cm) => {
        if (cm.somethingSelected()) {
          cm.indentSelection('add');
        } else {
          cm.execCommand('insertSoftTab');
        }
      },
    },
  };

  const readOnlyOptions = {
    mode: 'beancount',
    readOnly: true,
  };

  const queryOptions = {
    mode: 'beancount-query',
    extraKeys: {
      'Ctrl-Enter': () => {
        submitQuery();
      },
      'Cmd-Enter': () => {
        submitQuery();
      },
    },
  };

  // Read-only editors
  $$('.editor-readonly').forEach((el) => {
    CodeMirror.fromTextArea(el, readOnlyOptions);
  });

  // Query editor
  if ($('#query-editor')) {
    const editor = CodeMirror.fromTextArea($('#query-editor'), queryOptions);

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

  // The /source/ editor
  if ($('#source-editor')) {
    const el = $('#source-editor');
    const editor = CodeMirror.fromTextArea(el, defaultOptions);
    const saveButton = $('#source-editor-submit');

    editor.on('changes', (cm) => {
      saveButton.disabled = cm.isClean();
    });

    editor.on('keyup', (cm, event) => {
      if (!cm.state.completionActive && event.keyCode !== 13) {
        CodeMirror.commands.autocomplete(cm, null, { completeSingle: false });
      }
    });
    const line = parseInt(new URI(location.search).query(true).line, 10);
    if (line > 0) {
      editor.setCursor(line - 1, 0);
      centerCursor(editor);
    } else {
      jumpToMarker(editor);
    }

    $('#source-editor-select').addEventListener('change', (event) => {
      event.preventDefault();
      event.stopImmediatePropagation();
      const select = event.currentTarget;
      select.disabled = true;
      const filePath = select.value;

      const url = new URI(saveButton.getAttribute('data-url'))
        .setSearch('file_path', filePath)
        .toString();

      $.fetch(url)
        .then(handleJSON)
        .then((data) => {
          editor.setValue(data.payload);
          editor.setCursor(0, 0);
          jumpToMarker(editor);
        }, () => {
          e.trigger('error', _('Loading ${filePath} failed.', { filePath }));  // eslint-disable-line no-template-curly-in-string
        })
        .then(() => {
          select.disabled = false;
        });
    });

    // keybindings when the focus is outside the editor
    Mousetrap.bind(['ctrl+s', 'meta+s'], (event) => {
      event.preventDefault();
      saveEditorContent(editor);
    });

    Mousetrap.bind(['ctrl+d', 'meta+d'], (event) => {
      event.preventDefault();
      formatEditorContent(editor);
    });

    saveButton.addEventListener('click', (event) => {
      event.preventDefault();
      event.stopImmediatePropagation();
      saveEditorContent(editor);
    });

    $('#source-editor-format').addEventListener('click', (event) => {
      event.preventDefault();
      event.stopImmediatePropagation();
      formatEditorContent(editor);
    });
  }
}
