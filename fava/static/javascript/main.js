import { $, $$ } from './helpers';
import e from './events';

import initCharts from './charts';
import initClipboard from './clipboard';
import initDocumentsUpload from './documents-upload';
import initEditor from './editor';
import { initFilters, updateFilters } from './filters';
import initJournal from './journal';
import { initKeyboardShortcuts, updateKeyboardShortcuts } from './keyboard-shortcuts';
import initRouter from './router';
import initSort from './sort';
import initTreeTable from './tree-table';

const jQuery = require('jquery');

// These parts of the page should not change.
// So they only need to be initialized once.
function initPage() {
  initFilters();
  initKeyboardShortcuts();

  $$('.overlay-wrapper').forEach((el) => {
    el.addEventListener('click', (event) => {
      event.preventDefault();
      if (event.target.classList.contains('overlay-wrapper') ||
          event.target.classList.contains('close-overlay')) {
        el.classList.remove('shown');
      }
    });
  });

  $('#aside-button').addEventListener('click', (event) => {
    event.preventDefault();
    $('aside').classList.toggle('active');
    $('#aside-button').classList.toggle('active');
  });

  $.delegate($('#notifications'), 'click', 'li', (event) => {
    event.target.closest('li').remove();
  });
}

e.on('page-loaded', () => {
  updateFilters();
  updateKeyboardShortcuts();

  initCharts();
  initClipboard();
  initDocumentsUpload();
  initEditor();
  initJournal();
  initSort();
  initTreeTable();

  document.title = window.documentTitle;
  $('h1 strong').innerHTML = window.pageTitle;
  $('#reload-page').classList.add('hidden');

  $$('aside a').forEach((el) => {
    el.classList.remove('selected');
    if (el.getAttribute('href').startsWith(window.location.pathname)) {
      el.classList.add('selected');
    }
  });
});

e.on('file-modified', () => {
  fetch(`${window.baseURL}_aside/`)
    .then((response) => {
      response.text()
        .then((html) => {
          $('aside').innerHTML = html;
        });
    });
});

// Notifications
e.on('info', (msg) => {
  $('#notifications').insertAdjacentHTML('beforeend', `<li>${msg}</li>`);
});

e.on('error', (msg) => {
  $('#notifications').insertAdjacentHTML('beforeend', `<li class="error">${msg}</li>`);
});

function doPoll() {
  jQuery.get(`${window.baseURL}api/changed/`, (data) => {
    if (data.success && data.changed) {
      $('#reload-page').classList.remove('hidden');
      e.trigger('file-modified');
    }
  })
    .always(() => { setTimeout(doPoll, 5000); });
}

$.ready().then(() => {
  initPage();
  initRouter();
  e.trigger('page-loaded');
  setTimeout(doPoll, 5000);
});
