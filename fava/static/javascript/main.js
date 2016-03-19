require('jquery-query-object');
require('jquery-stupid-table/stupidtable');
require('jquery-dragster');

var charts = require('./charts');
var clipboard = require('./clipboard');
var filters = require('./filters');
var keyboardShortcuts = require('./keyboard-shortcuts');
var journal = require('./journal');
var treeTable = require('./tree-table');
var documentsUpload = require('./documents-upload');

// expose jquery to global context
window.$ = $

$(document).ready(function() {
    $("table.sortable").stupidtable();

    // Setup filters form
    filters.initFilters();

    // Global keyboard shortcuts
    keyboardShortcuts.global();

    // Tree-expanding
    if ($('table.tree-table').length) {
        treeTable.initTreeTable();
    };

    // Charts
    if ($('#chart-container').length) {
        charts.initCharts();
        keyboardShortcuts.charts();
    };

    // Journal
    if ($('#journal-table').length) {
        journal.initJournal();
        keyboardShortcuts.journal();
    };

    // Clipboard on statistics page
    if ($('#copy-balances').length) {
        clipboard.initClipboard();
    };

    // Documents upload
    if ($('table.tree-table').length || $('h1.droptarget').length) {
        documentsUpload.initDocumentsUpload();
    }

    // Overlays
    $('.overlay-wrapper').click(function(e) {
        e.preventDefault();
        if ($(e.target).hasClass('overlay-wrapper') || $(e.target).hasClass('close-overlay')) {
            $('.overlay-wrapper').hide();
        }
    });
});
