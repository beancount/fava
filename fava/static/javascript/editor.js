require('jquery-query-object');

require('ace-builds/src-min/ace');
require('ace-builds/src-min/ext-searchbox');
require('ace-builds/src-min/ext-language_tools');
require('./ace-mode-beancount.js');
require('ace-builds/src-min/mode-ini');
require('ace-builds/src-min/mode-sql');
require('ace-builds/src-min/theme-chrome');
require('ace-builds/src-min/ext-whitespace')

$(document).ready(function() {
    var defaultOptions = {
        theme: "ace/theme/chrome",
        mode: "ace/mode/beancount",
        wrap: true,
        printMargin: false,
        fontSize: "13px",
        fontFamily: "monospace",
        useSoftTabs: true,
        showFoldWidgets: true
    };

    if ($('.editor').attr('data-print-margin-column')) {
        defaultOptions['printMargin'] = true;
        defaultOptions['printMarginColumn'] = parseInt($('.editor').attr('data-print-margin-column'));
    }

    // Read-only editors
    $('.editor-wrapper .editor.editor-readonly').each(function() {
        var editorId = $(this).prop('id');
        var editor = ace.edit(editorId);
        editor.setOptions(defaultOptions);
        editor.setOptions({
            maxLines: editor.session.getLength(),
            readOnly: true,
            highlightActiveLine: false,
            highlightGutterLine: false
        });

        editor.renderer.$cursorLayer.element.style.opacity=0;

        if ($(this).hasClass('editor-async')) {
            $.get($(this).parents('form').attr('action'), { file_path: $(this).attr('data-file-path') })
            .done(function(data) {
                editor.setValue(data, -1);
                editor.setOptions({ maxLines: editor.session.getLength() });
            });
        }
    });

    // Query editor
    if ($('#editor-query').length) {
        var editor = ace.edit("editor-query");
        editor.setOptions(defaultOptions);
        editor.setOptions({
            mode: "ace/mode/sql",
        });

        editor.commands.addCommand({  // for when the focus is inside the editor
            name: "executeQuery",
            bindKey: {win: "Ctrl-Enter", mac: "Command-Enter"},
            exec: function(editor) {
                $('#submit-query').click();
            }
        });

        Mousetrap.bind(['ctrl+enter', 'meta+enter'], function(event) {  // for when the focus is outside the editor
            event.preventDefault();
            $('#submit-query').click();
        });

        $('#submit-query').click(function(event) {
            event.preventDefault();
            event.stopImmediatePropagation();
            var $button = $(this);
            $button.attr('disabled', 'disabled').attr('value', 'Submitting query...');
            var nextUrl = $button.parents('form').attr('action');
            nextUrl = nextUrl + (nextUrl.split('?')[1] ? '&' : '?') + "query_string=" + encodeURIComponent(editor.getValue());
            window.location.href = nextUrl;
        });

        $('.stored-queries select').change(function() {
            var sourceElement = $('.stored-queries a.source-link');
            var query = $(this).val();
            var sourceLink = $('option:selected', this).attr('data-source-link');

            editor.setValue(query, -1);
            sourceElement.attr('href', sourceLink).toggle(query != "");
        });
    };

    // The /source/ editor
    if ($('#editor-source').length) {
        var editorHeight = $(window).height() - $('header').outerHeight() - 110;
        $('.editor-wrapper').height(editorHeight);

        var editor = ace.edit("editor-source");
        var langTools = ace.require("ace/ext/language_tools");
        var whitespace = ace.require("ace/ext/whitespace");

        editor.setOptions(defaultOptions);

        var completionsAccounts = window.allAccounts.map(function (account) {
            return { name: account, value: account, score: 1, meta: "accounts" }
        });
        var completionsCommodities = window.allCommodities.map(function (commodity) {
            return { name: commodity, value: commodity, score: 2, meta: "commodities" }
        });
        var completionsDirectives = ['open', 'close', 'commodity', 'txn', 'balance', 'pad', 'note', 'document', 'price', 'event', 'option', 'plugin', 'include', 'query'].map(function (directive) {
            return { name: directive, value: directive, score: 3, meta: "directive" }
        });
        var completionsTags = window.allTags.map(function (tag) {
            return { name: '#' + tag, value: tag, score: 4, meta: "tags" }
        });
        var completions = completionsAccounts.concat(completionsCommodities, completionsDirectives);

        var beancountCompleter = {
            getCompletions: function(editor, session, pos, prefix, callback) {
                if (prefix.length === 0) { callback(null, []); return }
                if (prefix == '#') { callback(null, completionsTags); return }
                if (editor.session.getLine(pos.row).indexOf('#') > -1) { callback(null, completionsTags); return }
                if (editor.session.getLine(pos.row).indexOf('"') > -1) { callback(null, []); return }
                callback(null, completions);
            }
        }

        langTools.setCompleters([beancountCompleter]);
        editor.setOptions({enableLiveAutocompletion: true});

        editor.$blockScrolling = Infinity;
        editor.focus();

        var hlLine = $.query.get('line');
        $('form.editor-source select[name="file_path"]').change(function(event) {
            event.preventDefault();
            event.stopImmediatePropagation();
            var $select = $(this);
            $select.attr('disabled', 'disabled');
            $filePath = $select.val();
            $.get($select.parents('form').attr('action'), { file_path: $filePath } )
            .done(function(data) {
                if ($filePath != $.query.get('file_path')) {
                    hlLine = 1;
                }
                editor.setValue(data, -1);
                editor.gotoLine(hlLine, 0, true);
                $select.removeAttr('disabled');

                if ($filePath.endsWith('.conf') || $filePath.endsWith('.settings') || $filePath.endsWith('.ini')) {
                    editor.setOptions({mode: "ace/mode/ini"});
                    console.log($("input[name=config-file-defaults]").val());
                    console.log($filePath);
                } else {
                    editor.setOptions({mode: "ace/mode/beancount"});
                }

                $("form.editor-save").toggle($filePath != $("input[name=config-file-defaults]").val());

                if (window.editorInsertMarker && hlLine == 1) {
                    var range = editor.find(window.editorInsertMarker, {
                        wrap: true,
                        caseSensitive: false,
                        wholeWord: false,
                        regExp: false,
                        preventScroll: true // do not change selection
                    });

                    if (range) {
                        range.start.column = 0;
                        range.end.column = Number.MAX_VALUE;
                        editor.session.replace(range, "\n\n" + editor.session.getLine(range.start.row));
                        editor.gotoLine(range.start.row + 1, 0, true);
                    } else {
                        console.info("editor-insert-marker '" + window.editorInsertMarker + "' not found in file " + $filePath);
                    }
                }
            });
        });

        $('form.editor-source select[name="file_path"]').change();

        function saveEditorContent() {
            $(document).trigger('LiveReloadShutDown');

            if (window.editorStripTrailingWhitespace) {
                whitespace.trimTrailingSpace(editor.session, true);
            }

            var $button = $(this);
            var fileName = $('form.editor-source select').val();
            $button.attr('disabled', 'disabled').attr('value', 'Saving to ' + fileName + '...');
            var url = $button.parents('form').attr('action');
            $.post(url, { file_path: fileName, source: editor.getValue() } )
            .done(function(data) {
                if (data == "True") {
                    window.location = $.query
                                            .set('line', editor.getSelectionRange().start.row + 1)
                                            .set('file_path', fileName);
                } else {
                    alert("Writing to\n\n\t" + fileName + "\n\nwas not successful.");
                }
            });
        }

        editor.commands.addCommand({  // for when the focus is inside the editor
            name: "save",
            bindKey: {win: "Ctrl-S", mac: "Command-S"},
            exec: function(editor) {
                saveEditorContent();
            }
        });

        Mousetrap.bind(['ctrl+s', 'meta+s'], function(event) {  // for when the focus is outside the editor
            event.preventDefault();
            saveEditorContent();
        });

        $('form.editor-save input[type="submit"]').click(function(event) {
            event.preventDefault();
            event.stopImmediatePropagation();
            saveEditorContent();
        });
    }
});
