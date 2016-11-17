import CodeMirror from 'codemirror';
import URI from 'urijs';
import Mousetrap from 'mousetrap';

import 'codemirror/mode/sql/sql';
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

import './codemirror-fold-beancount';
import './codemirror-hint-beancount';
import './codemirror-mode-beancount';

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
      button.disabled = false;
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
    mode: 'text/x-sql',
    lineNumbers: true,
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

    // when the focus is outside the editor
    Mousetrap.bind(['ctrl+enter', 'meta+enter'], (event) => {
      event.preventDefault();
      submitQuery();
    });

    const select = $('.stored-queries select');
    select.addEventListener('change', () => {
      const sourceElement = $('.stored-queries a.source-link');
      const sourceLink = select.options[select.selectedIndex].getAttribute('data-source-link');

      editor.setValue(select.value);
      sourceElement.setAttribute('href', sourceLink);
      sourceElement.classList.toggle('hidden', select.value === '');
    });
  }

  // The /source/ editor
  if ($('#source-editor')) {
    const el = $('#source-editor');
    const editor = CodeMirror.fromTextArea(el, defaultOptions);

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

      const url = new URI($('#source-editor-submit').getAttribute('data-url'))
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

    $('#source-editor-submit').addEventListener('click', (event) => {
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
