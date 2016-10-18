import 'jquery-stupid-table/stupidtable';

import e from './events';
import initCharts from './charts';
import initClipboard from './clipboard';
import initDocumentsUpload from './documents-upload';
import initEditor from './editor';
import { initFilters, updateFilters } from './filters';
import initJournal from './journal';
import { initKeyboardShortcuts, updateKeyboardShortcuts } from './keyboard-shortcuts';
import initRouter from './router';
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

e.on('page-loaded', () => {
  updatePage();

  document.title = window.documentTitle;
  $('h1 strong').html(window.pageTitle);
  document.getElementById('reload-page').classList.add('hidden');

  $('aside a').each((_, el) => {
    el.classList.remove('selected');
    if (el.getAttribute('href').startsWith(window.location.pathname)) {
      el.classList.add('selected');
    }
  });
});

e.on('file-modified', () => {
  $('aside').load(`${window.location.pathname} aside`);
});

// Notifications
e.on('info', (msg) => {
  $('#notifications').append(`<li>${msg}</li>`);
});

e.on('error', (msg) => {
  $('#notifications').append(`<li class="error">${msg}</li>`);
});

function doPoll() {
  $.get(window.changedUrl, (data) => {
    if (data.success && data.changed) {
      document.getElementById('reload-page').classList.remove('hidden');
      e.trigger('file-modified');
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
