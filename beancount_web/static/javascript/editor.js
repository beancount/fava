$(document).ready(function() {
    // Editor
    var editorHeight = $('.main').height() - 60;
    $('#editor-wrapper').height(editorHeight);

    var editor = ace.edit("editor");
    editor.setTheme("ace/theme/chrome");
    editor.setOption('wrap', true);
    editor.setOption('printMargin', false);
    editor.setOption('fontSize', "13px");
    editor.setOption('fontFamily', "monospace");
    editor.getSession().setMode("ace/mode/beancount");

    $.hlLine = $.urlParam('hl_line');
    $('form.editor-source select').change(function(event) {
        event.preventDefault();
        var $this = $(this);
        $.get($(this).parents('form').attr('action'), { file_path: $(this).val(), is_ajax: true } )
        .done(function(data) {
            editor.setValue(data, -1);
            editor.gotoLine($.hlLine, 1, true);
            $.hlLine = 1;
        });
    });

    $('form.editor-source select:first-child').change();

    $('form.editor-save input[type="submit"]').click(function(event) {
        event.preventDefault();
        var $this = $(this);
        var fileName = $('form.editor-source select').val();

        $.post($(this).parents('form').attr('action'), { file_path: fileName, source: editor.getValue() } )
        .done(function(data) {
            if (data == "True") {
                alert("Successfully saved to\n\n\t" + fileName + "\n\nReloading files...");
                location.reload();
            } else {
                alert("Writing to\n\n\t" + fileName + "\n\nwas not successful.");
            }
        });

    });
});



