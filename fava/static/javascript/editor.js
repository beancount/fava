require('jquery-query-object');

require('ace-builds/src-min/ace');
require('ace-builds/src-min/ext-searchbox');
require('ace-builds/src-min/ext-language_tools');
require('./ace-mode-beancount.js');
require('ace-builds/src-min/mode-sql');
require('ace-builds/src-min/theme-chrome');

$(document).ready(function() {
    var defaultOptions = {
        theme: "ace/theme/chrome",
        mode: "ace/mode/beancount",
        wrap: true,
        printMargin: false,
        fontSize: "13px",
        fontFamily: "monospace",
        useSoftTabs: true,
        showFoldWidgets: false
    };

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

        $('form.editor-save input[type="submit"]').click(function(event) {
            event.preventDefault();
            event.stopImmediatePropagation();
            var $button = $(this);
            $button.attr('disabled', 'disabled').attr('value', 'Submitting query...');
            var nextUrl = $button.parents('form').attr('action') + "?bql=" + encodeURIComponent(editor.getValue());
            var storedQuerySelectedIndex = $('.stored-queries select').prop('selectedIndex');
            if (storedQuerySelectedIndex > 0) {
                var storedQueryHash = $('.stored-queries select option:nth-child(' + (storedQuerySelectedIndex + 1) + ')').attr('data-stored-query-hash');
                nextUrl = nextUrl + '&query_hash=' + storedQueryHash;
            }
            window.location.href = nextUrl;
        });

        $('.stored-queries select').change(function() {
            var selected_id_url = $(this).val();
            if (selected_id_url != "") {
                $.get(selected_id_url)
                .done(function(data) {
                    editor.setValue(data, -1);
                });
            } else {
                editor.setValue("", -1);
            }
        });
    };

    // The /source/ editor
    if ($('#editor-source').length) {
        var editorHeight = $(window).height() - $('header').outerHeight() - 110;
        $('.editor-wrapper').height(editorHeight);

        var editor = ace.edit("editor-source");
        var langTools = ace.require("ace/ext/language_tools");

        editor.setOptions(defaultOptions);

        var completionsAccounts = window.allAccounts.map(function (account) {
            return { name: account, value: account, score: 1, meta: "accounts" }
        });
        var completionsCommodities = window.allCommodities.map(function (commodity) {
            return { name: commodity, value: commodity, score: 2, meta: "commodities" }
        });
        var completionsDirectives = ['open', 'close', 'commodity', 'txn', 'balance', 'pad', 'note', 'document', 'price', 'event', 'option', 'plugin', 'include'].map(function (directive) {
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

        $('form.editor-save input[type="submit"]').click(function(event) {
            event.preventDefault();
            event.stopImmediatePropagation();
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
        });
    }
});
