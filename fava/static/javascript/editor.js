/* global Mousetrap */

// TODO:
//
// - soft tabs ?
// - trim trailing whitespace (plus highlighting)
//
//
const URI = require('urijs');

const CodeMirror = require('codemirror/lib/codemirror');

require('codemirror/mode/sql/sql');
require('codemirror/addon/mode/simple');

// search
require('codemirror/addon/dialog/dialog');
require('codemirror/addon/search/searchcursor');
require('codemirror/addon/search/search');

// print margin
require('codemirror/addon/display/rulers');

// folding
require('codemirror/addon/fold/foldcode');
require('codemirror/addon/fold/foldgutter');
require('./codemirror-fold-beancount.js');

// auto-complete
require('codemirror/addon/hint/show-hint');
require('./codemirror-hint-beancount.js');

require('./codemirror-mode-beancount.js');

function fireEvent(element, eventName) {
  const event = document.createEvent('HTMLEvents');
  event.initEvent(eventName, true, true);
  return document.dispatchEvent(event);
}

function saveEditorContent(cm) {
  // trim trailing whitespace here

  const $button = $('#source-editor-submit');
  const fileName = $('#source-editor-select').val();
  $button
      .attr('disabled', 'disabled')
      .attr('value', `Saving to ${fileName}...`);
  const url = $button.parents('form').attr('action');
  $.post(url, {
    file_path: fileName,
    source: cm.getValue(),
  })
    .done((data) => {
      if (data !== 'True') {
        alert(`Writing to\n\n\t${fileName}\n\nwas not successful.`);
      } else {
        $button
            .removeAttr('disabled')
            .attr('value', 'Save');
      }
    });
}

$(document).ready(() => {
  const rulers = [];
  if (window.editorPrintMarginColumn) {
    rulers.push({
      column: window.editorPrintMarginColumn,
      lineStyle: 'dotted',
    });
  }

  const defaultOptions = {
    mode: 'beancount',
    lineNumbers: true,
    rulers,
    foldGutter: true,
    gutters: ['CodeMirror-linenumbers', 'CodeMirror-foldgutter'],
    extraKeys: {
      'Ctrl-Space': 'autocomplete',
      'Ctrl-S': (cm) => {
        saveEditorContent(cm);
      },
      'Cmd-S': (cm) => {
        saveEditorContent(cm);
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
        $('#submit-query').click();
      },
      'Cmd-Enter': () => {
        $('#submit-query').click();
      },
    },
  };

  // Read-only editors
  $('.editor-readonly').each((i, el) => {
    CodeMirror.fromTextArea(el, readOnlyOptions);
  });

  // Query editor
  if ($('#query-editor').length) {
    fireEvent(document, 'LiveReloadShutDown');

    const editor = CodeMirror.fromTextArea(document.getElementById('query-editor'), queryOptions);

    // when the focus is outside the editor
    Mousetrap.bind(['ctrl+enter', 'meta+enter'], (event) => {
      event.preventDefault();
      $('#submit-query').click();
    });

    $('.stored-queries select').change((event) => {
      const sourceElement = $('.stored-queries a.source-link');
      const query = $(event.currentTarget).val();
      const sourceLink = $('option:selected', event.currentTarget).attr('data-source-link');

      editor.setValue(query);
      sourceElement.attr('href', sourceLink).toggle(query !== '');
    });
  }

  // The /source/ editor
  if ($('#source-editor').length) {
    fireEvent(document, 'LiveReloadShutDown');

    const el = document.getElementById('source-editor');
    const editor = CodeMirror.fromTextArea(el, defaultOptions);

    editor.on('keyup', (cm, event) => {
      if (!cm.state.completionActive && event.keyCode !== 13) {
        CodeMirror.commands.autocomplete(cm, null, { completeSingle: false });
      }
    });
    const line = parseInt(new URI(location.search).query(true).line, 10);
    if (line > 0) {
      editor.setCursor(line - 1, 0);
    }

    $('#source-editor-select').change((event) => {
      event.preventDefault();
      event.stopImmediatePropagation();
      const $select = $(event.currentTarget);
      $select.attr('disabled', 'disabled');
      const filePath = $select.val();
      $.get($select.parents('form').attr('action'), {
        file_path: filePath,
      })
        .done((data) => {
          editor.setValue(data);
          editor.setCursor(0, 0);
          $select.removeAttr('disabled');

          if (filePath.endsWith('.conf') ||
              filePath.endsWith('.settings') ||
              filePath.endsWith('.ini')) {
            editor.setOption('mode', 'text/x-ini');
          } else {
            editor.setOption('mode', 'beancount');
          }

          if (window.editorInsertMarker) {
            const cursor = editor.getSearchCursor(window.editorInsertMarker);

            if (cursor.findNext()) {
              editor.focus();
              editor.setCursor(cursor.pos.from);
              editor.execCommand('goLineUp');
            }
          }
        });
    });

    // keybindings when the focus is outside the editor
    Mousetrap.bind(['ctrl+s', 'meta+s'], (event) => {
      event.preventDefault();
      saveEditorContent(editor);
    });

    $('#source-editor-submit').click((event) => {
      event.preventDefault();
      event.stopImmediatePropagation();
      saveEditorContent(editor);
    });
  }
});
