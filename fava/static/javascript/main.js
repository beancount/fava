require('jquery-stupid-table/stupidtable');
require('jquery-dragster');
const Backbone = require('backbone');
const URI = require('urijs');

const charts = require('./charts');
const clipboard = require('./clipboard');
const editor = require('./editor');
const filters = require('./filters');
const keyboardShortcuts = require('./keyboard-shortcuts');
const journal = require('./journal');
const treeTable = require('./tree-table');
const documentsUpload = require('./documents-upload');

function getFormatFromUrl(url) {
  const dotIndex = url.indexOf('.');
  return (dotIndex > 0) ? url.slice(dotIndex + 1) : 'html';
}

function initPage() {
  $('table.sortable').stupidtable();

  filters.initFilters();
  keyboardShortcuts.global();

  if ($('.tree-table').length) {
    treeTable.initTreeTable();
  }

  if ($('#chart-container').length) {
    charts.initCharts();
    keyboardShortcuts.charts();
  }

  editor.initEditor();

  if ($('#journal-table').length) {
    journal.initJournal();
    keyboardShortcuts.journal();
  }

  if ($('.status-indicator').length) {
    clipboard.initClipboard();
  }

  if ($('.tree-table').length || $('h1.droptarget').length) {
    documentsUpload.initDocumentsUpload();
  }

  $('.overlay-wrapper').click((e) => {
    e.preventDefault();
    if ($(e.target).hasClass('overlay-wrapper') || $(e.target).hasClass('close-overlay')) {
      $('.overlay-wrapper').hide();
    }
  });

  $('#aside-button').click((e) => {
    e.preventDefault();
    $('aside').toggleClass('active');
    $('#aside-button').toggleClass('active');
    return false;
  });
}

const Router = Backbone.Router.extend({
  initialize() {
    this.isFirstRoute = true;
  },
  routes: {
    '*path': 'replaceArticle',
  },
  replaceArticle() {
    if (this.isFirstRoute) {
      this.isFirstRoute = false;
      return;
    }

    $.get(`/${Backbone.history.fragment}`, { partial: true }, (data) => {
      $('article').html(data);
      initPage();
      $('h1').html(window.h1Html);
    });
  },
});

const app = new Router();

function cleanURL(url) {
  const newURL = new URI(url)
    .search($('#filter-form').serialize());
  if ($('#chart-interval').length) {
    newURL
      .setSearch('interval', $('#chart-interval').val());
  }
  return newURL.toString();
}

function initRouter() {
  Backbone.history.start({ pushState: true });

  $(document).on('click', 'a', (event) => {
    const $link = $(event.currentTarget);
    const href = $link.attr('href');

    const isHttp = $link.prop('protocol').indexOf('http') === 0;
    const format = getFormatFromUrl(href);

    if (!event.isDefaultPrevented() && isHttp && format === 'html') {
      event.preventDefault();
      $('.selected').removeClass('selected');
      $link.addClass('selected');

      cleanURL(href);
      app.navigate(cleanURL(href), { trigger: true });
    }
  });

  $(document).on('submit', '#filter-form', (event) => {
    event.preventDefault();
    app.navigate(cleanURL(Backbone.history.location.pathname), { trigger: true });
  });

  $(document).on('change', '#chart-interval', (event) => {
    event.preventDefault();
    app.navigate(cleanURL(Backbone.history.location.pathname), { trigger: true });
  });
}

$(document).ready(() => {
  initPage();
  initRouter();
});
