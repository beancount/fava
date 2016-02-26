require('jquery-query-object');
require('jquery-stupid-table/stupidtable');
require('jquery-dragster');

window.Mousetrap = require('mousetrap');
require('mousetrap/plugins/bind-dictionary/mousetrap-bind-dictionary');

var charts = require('./charts');
var clipboard = require('./clipboard');
var filters = require('./filters');
var journal = require('./journal');
var treeTable = require('./tree-table');

// expose jquery to global context
window.$ = $

$(document).ready(function() {
    $("table.sortable").stupidtable();

    // Setup filters form
    filters.initFilters();

    // Tree-expanding
    if ($('table.tree-table').length) {
        treeTable.initTreeTable();
    };

    // Charts
    if ($('#chart-container').length) {
        charts.initCharts();
    };

    // Journal
    if ($('#journal-table').length) {
        journal.initJournal();
    };

    // Clipboard on statistics page
    if ($('#copy-balances').length) {
        clipboard.initClipboard();
    };

    function uploadDocuments(formData, filename, targetFolderIndex) {
        formData.append('filename', filename);
        formData.append('targetFolderIndex', targetFolderIndex);

        $.ajax({
            type: 'POST',
            url: window.documentsUploadUrl,
            data: formData,
            contentType: false,
            cache: false,
            processData: false,
            async: false,
            success: function(data) {
                alert(data);
            },
            error: function() {
                alert("Error while uploading.")
            }
        });
    }

    // File uploads via Drag and Drop on elements with class "droptarget" and
    // attribute "data-account-name"
    if (window.documentsFolders.length > 0) {
        $('.droptarget').bind({
            dragenter: function(e) {
                e.stopPropagation();
                e.preventDefault();
            },

            dragover: function(e) {
                e.stopPropagation();
                e.preventDefault();
            },

            drop: function(e) {
                e.preventDefault();
                var files = e.originalEvent.dataTransfer.files;

                for (var i = 0; i < files.length; i++) {
                    var formData = new FormData();
                    console.log(files[i]);
                    formData.append('file', files[i]);
                    formData.append('account_name', $(this).attr('data-account-name'));

                    var filename = files[i].name;
                    var filenameRegex = /^\d{4}-\d{1,2}-\d{1,2}\.$/;

                    if (filename.length < 11 || filenameRegex.test(filename.substring(0, 11)) == false) {
                        var today = new Date();
                        filename = today.toISOString().substring(0, 10) + '.' + filename;
                    }

                    $('#documents-upload input#document-name').val(filename);
                    $('#documents-upload input[type="submit"]').click(function(event) {
                        event.preventDefault();
                        var documentFolderIndex = $('#documents-upload select#document-upload-folder').val();
                        uploadDocuments(formData, filename, documentFolderIndex);
                        $('.overlay-wrapper').hide();
                    });

                    if (window.documentsFolders.length <= 1) {
                        $('#documents-upload select#document-upload-folder').hide();
                        $('#documents-upload label#label-documents-upload-folder').hide();
                    }

                    if (filename == files[i].name) {
                        $('#documents-upload input#document-name').hide();
                        $('#documents-upload label#label-document-name').hide();
                    }

                    if (window.documentsFolders.length > 1 || filename != files[i].name) {
                        $('#documents-upload').show();
                    } else {
                        uploadDocuments(formData, filename, 0)
                    }
                }
            }
        });
    }

    $('.droptarget').dragster({
        enter: function (dragsterEvent, event) {
            $(this).addClass('dragover');
        },
        leave: function (dragsterEvent, event) {
            $(this).removeClass('dragover');
        },
        drop: function (dragsterEvent, event) {
            $(this).removeClass('dragover');
        }
    });

    // Keyboard shortcuts

    // Jumping through charts
    if ($('#chart-labels').length) {
        Mousetrap.bind({
            'shift+c': function() { $('#toggle-chart').click(); },
            'c':       function() {
                var next = $('#chart-labels label.selected').next();
                $('#chart-labels label').removeClass('selected');
                if (next.length) { next.click(); }
                else             { $('#chart-labels label:first-child').click(); }
            },

        }, 'keyup');
    }

    // Options in transaction pages:
    if ($('#entry-filters').length) {
        Mousetrap.bind({
            'l':   function() { $('#toggle-legs').click(); },
            'm':   function() { $('#toggle-metadata').click(); },

            's o': function() { $('#filter-open').click(); },
            's c': function() { $('#filter-close').click(); },
            's t': function() { $('#filter-transaction').click(); },
            's b': function() { $('#filter-balance').click(); },
            's n': function() { $('#filter-note').click(); },
            's d': function() { $('#filter-document').click(); },
            's p': function() { $('#filter-pad').click(); },

            't c': function() { $('#filter-cleared').click(); },
            't p': function() { $('#filter-pending').click(); },
            't shift+p': function() { $('#filter-padding').click(); },
            't s': function() { $('#filter-summarize').click(); },
            't t': function() { $('#filter-transfer').click(); },
            't o': function() { $('#filter-other').click(); },
        }, 'keyup');
    }

    Mousetrap.bind({
        '?': function() { $('#keyboard-shortcuts.overlay-wrapper').show(); },
        'esc': function() { $('.overlay-wrapper').hide(); }
    }, 'keyup');

    // Overlays
    $('.overlay-wrapper').click(function(e) {
        e.preventDefault();
        if ($(e.target).hasClass('overlay-wrapper') || $(e.target).hasClass('close-overlay')) {
            $('.overlay-wrapper').hide();
        }
    });
});
