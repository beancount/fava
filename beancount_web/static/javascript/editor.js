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
            window.location.href = $button.parents('form').attr('action') + "?bql=" + encodeURIComponent(editor.getValue());
        });
    };

    // The /source/ editor
    if ($('#editor-source').length) {
        var editorHeight = $(window).height() - $('header').outerHeight() - 110;
        $('.editor-wrapper').height(editorHeight);

        var editor = ace.edit("editor-source");
        editor.setOptions(defaultOptions);
        editor.$blockScrolling = Infinity;
        editor.focus();

        var hlLine = $.urlParamWindow('line');
        $('form.editor-source select[name="file_path"]').change(function(event) {
            event.preventDefault();
            event.stopImmediatePropagation();
            var $select = $(this);
            $select.attr('disabled', 'disabled');
            $filePath = $select.val();
            $.get($select.parents('form').attr('action'), { file_path: $filePath, is_ajax: true } )
            .done(function(data) {
                editor.setValue(data, -1);
                editor.gotoLine(hlLine, 1, true);
                if ($filePath != $.urlParamWindow('file_path')) {
                    hlLine = 1;
                }
                $select.removeAttr('disabled');
            });
        });

        $('form.editor-source select[name="file_path"]').change();

        $('form.editor-save input[type="submit"]').click(function(event) {
            event.preventDefault();
            event.stopImmediatePropagation();
            var $button = $(this);
            $button.attr('disabled', 'disabled').attr('value', 'Saving...');
            var fileName = $('form.editor-source select').val();
            $.post($button.parents('form').attr('action'), { file_path: fileName, source: editor.getValue() } )
            .done(function(data) {
                if (data == "True") {
                    alert("Successfully saved to\n\n\t" + fileName + "\n\nReloading files...");
                    location.reload();
                } else {
                    alert("Writing to\n\n\t" + fileName + "\n\nwas not successful.");
                }
            });
        });
    }
});
