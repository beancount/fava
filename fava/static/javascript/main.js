require('jquery-stupid-table/stupidtable');
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

// These parts of the page should not change.
// So they only need to be initialized once.
function initPage() {
  filters.init();
  keyboardShortcuts.init();

  $('.overlay-wrapper').click((event) => {
    event.preventDefault();
    if ($(event.target).hasClass('overlay-wrapper') || $(event.target).hasClass('close-overlay')) {
      $('.overlay-wrapper').removeClass('shown');
    }
  });

  $('#aside-button').click((event) => {
    event.preventDefault();
    $('aside').toggleClass('active');
    $('#aside-button').toggleClass('active');
  });

  $('#notifications').on('click', 'li', (event) => {
    $(event.currentTarget).remove();
  });
}

function updatePage() {
  filters.update();
  $('table.sortable').stupidtable();
  keyboardShortcuts.update();

  treeTable.initTreeTable();

  if ($('#chart-container').length) {
    charts.initCharts();
  }

  editor.initEditor();

  if ($('#journal-table').length) {
    journal.initJournal();
  }

  if ($('.status-indicator').length) {
    clipboard.initClipboard();
  }

  if ($('.tree-table').length || $('h1.droptarget').length) {
    documentsUpload.initDocumentsUpload();
  }
}

// Notifications
Backbone.on('info', (msg) => {
  $('#notifications').append(`<li>${msg}</li>`);
});

Backbone.on('error', (msg) => {
  $('#notifications').append(`<li class="error">${msg}</li>`);
});

const Router = Backbone.Router.extend({
  initialize() {
    this.isFirstRoute = true;
    this.listenTo(Backbone, 'file-modified', () => {
      $('aside').load(`/${Backbone.history.fragment} aside`);
    });
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
      updatePage();
      document.title = window.documentTitle;
      $('h1 strong').html(window.pageTitle);
      $('#reload-page').addClass('hidden');
    });
  },
});

const app = new Router();

function updateURL(url) {
  const newURL = new URI(url);
  $.each(['account', 'from', 'payee', 'tag', 'time'], (_, filter) => {
    newURL.removeSearch(filter);
    if ($(`#${filter}-filter`).val()) {
      newURL.setSearch(filter, $(`#${filter}-filter`).val());
    }
  });
  const $interval = $('#chart-interval');
  if ($interval.length) {
    newURL.setSearch('interval', $interval.val());
    if ($interval.val() === $interval.data('default')) {
      newURL.removeSearch('interval');
    }
  }
  return newURL.toString();
}

function initRouter() {
  Backbone.history.start({ pushState: true });

  $(document).on('click', 'a', (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) {
      return;
    }
    const $link = $(event.currentTarget);
    let href = $link.attr('href');

    const isHttp = $link.prop('protocol').indexOf('http') === 0;
    const format = (href.indexOf('.') > 0) ? href.slice(href.indexOf('.') + 1) : 'html';
    const isRemote = $link.data('remote');

    if (!event.isDefaultPrevented() && !isRemote && isHttp && format === 'html') {
      event.preventDefault();
      $('.selected').removeClass('selected');
      $link.addClass('selected');

      // update sidebar links
      if (!$link.data('no-update') && $link.parents()[2].tagName === 'ASIDE') {
        href = updateURL(href);
      }
      app.navigate(href, { trigger: true });
    }
  });

  $('#reload-page').click((event) => {
    event.preventDefault();
    app.replaceArticle();
  });

  $(document).on('submit', '#filter-form', (event) => {
    event.preventDefault();
    app.navigate(updateURL(Backbone.history.location.pathname), { trigger: true });
  });

  $(document).on('submit', '#query-form', (event) => {
    event.preventDefault();
    const url = new URI(`/${Backbone.history.fragment}`)
      .setSearch('query_string', $('#query-editor').val())
      .toString();
    $.get(url, { partial: true, result_only: true }, (data) => {
      $('#query-container').html(data);
    });
  });

  $(document).on('change', '#chart-interval', (event) => {
    event.preventDefault();
    app.navigate(updateURL(Backbone.history.location.pathname), { trigger: true });
  });
}

function doPoll() {
  $.get(window.changedUrl, (data) => {
    if (data.success && data.changed) {
      $('#reload-page').removeClass('hidden');
      Backbone.trigger('file-modified');
    }
  })
    .always(() => { setTimeout(doPoll, 5000); });
}

$(document).ready(() => {
  initPage();
  updatePage();
  initRouter();
  setTimeout(doPoll, 5000);
});
