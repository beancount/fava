import 'es6-promise';
import 'whatwg-fetch';
import 'classlist.js';
import 'element-closest';

import { $, $$, _, handleJSON } from './helpers';
import e from './events';
import './../css/style.css';

import initCharts from './charts';
import initClipboard from './clipboard';
import initDocumentsUpload from './documents-upload';
import initEditor from './editor';
import { initFilters, updateFilters } from './filters';
import initIngest from './ingest';
import initJournal from './journal';
import { initKeyboardShortcuts, updateKeyboardShortcuts } from './keyboard-shortcuts';
import initRouter from './router';
import initSort from './sort';
import initTransactionOverlay from './transaction-overlay';
import initTreeTable from './tree-table';
import initEntryForms from './entry-forms';

// These parts of the page should not change.
// So they only need to be initialized once.
function initPage() {
  window.favaTranslations = JSON.parse($('#translations').innerHTML);
  initFilters();
  initKeyboardShortcuts();
  initTransactionOverlay();
  initIngest();
  initEntryForms();

  $$('.overlay-wrapper').forEach((el) => {
    el.addEventListener('mousedown', (event) => {
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

let pageData;

function initSidebar() {
  $$('aside a').forEach((el) => {
    el.classList.remove('selected');
    if (el.getAttribute('href').startsWith(window.location.pathname)) {
      el.classList.add('selected');
    }
  });
  $('aside li.error').classList.toggle('hidden', pageData.errors === 0);
  $('aside li.error span').innerHTML = pageData.errors;
}

e.on('page-loaded', () => {
  window.favaAPI = JSON.parse($('#ledger-data').innerHTML);
  updateFilters();
  updateKeyboardShortcuts();

  initCharts();
  initClipboard();
  initDocumentsUpload();
  initEditor();
  initJournal();
  initSort();
  initTreeTable();

  pageData = JSON.parse($('#page-data').innerHTML);
  document.title = pageData.documentTitle;
  $('h1 strong').innerHTML = pageData.pageTitle;
  $('#reload-page').classList.add('hidden');
  initSidebar();
});

e.on('file-modified', () => {
  $.fetch(`${window.favaAPI.baseURL}api/errors/`)
    .then(handleJSON)
    .then((data) => {
      pageData.errors = data.errors;
      initSidebar();
    });
});

// Notifications
e.on('info', (msg) => {
  $('#notifications').insertAdjacentHTML('beforeend', `<li>${msg}</li>`);
});

e.on('reload-warning', (msg) => {
  $('#notifications').insertAdjacentHTML('beforeend', `<li class="warning">${msg}</li>`);
  const warning = $('#notifications').lastChild;
  warning.addEventListener('click', (event) => {
    event.preventDefault();
    warning.remove();
    e.trigger('reload');
  });
  setTimeout(() => {
    warning.remove();
  }, 5000);
});

e.on('error', (msg) => {
  $('#notifications').insertAdjacentHTML('beforeend', `<li class="error">${msg}</li>`);
});

function doPoll() {
  $.fetch(`${window.favaAPI.baseURL}api/changed/`)
    .then(handleJSON)
    .then((data) => {
      if (data.changed) {
        if (window.favaAPI.favaOptions['auto-reload']) {
          e.trigger('reload');
        } else {
          $('#reload-page').classList.remove('hidden');
          e.trigger('file-modified');
          e.trigger('reload-warning', _('File change detected. Click to reload.'));
        }
      }
    }, () => {})
    .then(() => {
      setTimeout(doPoll, 5000);
    });
}

$.ready().then(() => {
  initPage();
  initRouter();
  e.trigger('page-loaded');
  setTimeout(doPoll, 5000);
});
