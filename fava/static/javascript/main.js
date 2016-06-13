require('jquery-stupid-table/stupidtable');
require('jquery-dragster');

const charts = require('./charts');
const clipboard = require('./clipboard');
const filters = require('./filters');
const keyboardShortcuts = require('./keyboard-shortcuts');
const journal = require('./journal');
const treeTable = require('./tree-table');
const documentsUpload = require('./documents-upload');

// expose jquery to global context
window.$ = $;

$(document).ready(() => {
  $('table.sortable').stupidtable();

  // Setup filters form
  filters.initFilters();

  // Global keyboard shortcuts
  keyboardShortcuts.global();

  // Tree-expanding
  if ($('.tree-table').length) {
    treeTable.initTreeTable();
  }

  // Charts
  if ($('#chart-container').length) {
    charts.initCharts();
    keyboardShortcuts.charts();
  }

  // Journal
  if ($('#journal-table').length) {
    journal.initJournal();
    keyboardShortcuts.journal();
  }

  // Clipboard
  if ($('.status-indicator').length) {
    clipboard.initClipboard();
  }

  // Documents upload
  if ($('.tree-table').length || $('h1.droptarget').length) {
    documentsUpload.initDocumentsUpload();
  }

  // Overlays
  $('.overlay-wrapper').click((e) => {
    e.preventDefault();
    if ($(e.target).hasClass('overlay-wrapper') || $(e.target).hasClass('close-overlay')) {
      $('.overlay-wrapper').hide();
    }
  });

  $('#aside_button').click((e) => {
    e.preventDefault();
    $("aside").toggleClass("active");
    $("#aside_button").toggleClass("active");
    return false;
  });
});
