import Backbone from 'backbone';
import URI from 'urijs';
import 'jquery-stupid-table/stupidtable';

import initCharts from './charts';
import initClipboard from './clipboard';
import initDocumentsUpload from './documents-upload';
import initEditor from './editor';
import { initFilters, updateFilters } from './filters';
import initJournal from './journal';
import { initKeyboardShortcuts, updateKeyboardShortcuts } from './keyboard-shortcuts';
import initTreeTable from './tree-table';

// These parts of the page should not change.
// So they only need to be initialized once.
function initPage() {
  initFilters();
  initKeyboardShortcuts();

  $('.overlay-wrapper').click((event) => {
    event.preventDefault();
    if (event.target.classList.contains('overlay-wrapper') ||
        event.target.classList.contains('close-overlay')) {
      $('.overlay-wrapper').removeClass('shown');
    }
  });

  $('#aside-button').click((event) => {
    event.preventDefault();
    $('aside').toggleClass('active');
    $('#aside-button').toggleClass('active');
  });

  $('#notifications').on('click', 'li', (event) => {
    event.currentTarget.remove();
  });
}

function updatePage() {
  updateFilters();
  $('table.sortable').stupidtable();
  updateKeyboardShortcuts();

  initCharts();
  initClipboard();
  initDocumentsUpload();
  initEditor();
  initJournal();
  initTreeTable();
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
  ['account', 'from', 'payee', 'tag', 'time'].forEach((filter) => {
    newURL.removeSearch(filter);
    const el = document.getElementById(`${filter}-filter`);
    if (el.value) {
      newURL.setSearch(filter, el.value);
    }
  });
  const interval = document.getElementById('chart-interval');
  if (interval) {
    newURL.setSearch('interval', interval.value);
    if (interval.value === interval.dataset.default) {
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
    const link = event.currentTarget;
    let href = link.getAttribute('href');

    const isHttp = link.protocol.indexOf('http') === 0;
    const format = (href.indexOf('.') > 0) ? href.slice(href.indexOf('.') + 1) : 'html';
    const isRemote = link.dataset.remote;

    if (!event.isDefaultPrevented() && !isRemote && isHttp && format === 'html') {
      event.preventDefault();
      $('.selected').removeClass('selected');
      link.classList.add('selected');

      // update sidebar links
      if (link.parentNode.parentNode.parentNode.tagName === 'ASIDE') {
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
