// Fava's main Javascript entry point.
//
// The code for Fava's UI is split into several modules that are all imported
// below. The different modules can listen to and register events to
// communicate and to register DOM event handlers for example.
//
// The events currently in use in Fava:
//
// error, info, reload-warning:
//    Trigger with a single message argument to display notifications of the
//    given type in the top right corner of the page.
//
// file-modified:
//    Fetch and update the error count in the sidebar.
//
// page-init:
//    Run once the page is initialized, i.e., when the DOM is ready. Use this
//    for JS code and parts of the UI that are independent of the current
//    contents of <article>.
//
// page-loaded:
//    After a new page has been loaded asynchronously. Use this to bind to
//    elements in the page.
//
// reload:
//    This triggers a reload of the page.
//

// Polyfills
import 'es6-promise';
import 'whatwg-fetch';
import 'classlist.js';
import 'element-closest';

import { $, $$, _, handleJSON } from './helpers';
import e from './events';
import initRouter from './router';
import './../css/style.css';

import './charts';
import './clipboard';
import './documents-upload';
import './editor';
import './entry-forms';
import './filters';
import './ingest';
import './journal';
import './keyboard-shortcuts';
import './sidebar';
import './sort';
import './transaction-overlay';
import './tree-table';

e.on('page-init', () => {
  window.favaTranslations = JSON.parse($('#translations').innerHTML);

  $$('.overlay-wrapper').forEach((el) => {
    el.addEventListener('mousedown', (event) => {
      if (event.target.classList.contains('overlay-wrapper') ||
          event.target.classList.contains('close-overlay')) {
        el.classList.remove('shown');
        window.location.hash = '';
      }
    });
  });

  $.delegate($('#notifications'), 'click', 'li', (event) => {
    event.target.closest('li').remove();
  });
});

e.on('page-loaded', () => {
  window.favaAPI = JSON.parse($('#ledger-data').innerHTML);
  document.title = $('#data-document-title').value;
  $('h1 strong').innerHTML = $('#data-page-title').value;
  $('#reload-page').classList.add('hidden');
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

// Check the `changed` API endpoint every 5 seconds and fire the appropriate
// events if some file changed.
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
  window.favaAPI = JSON.parse($('#ledger-data').innerHTML);
  initRouter();
  e.trigger('page-init');
  e.trigger('page-loaded');
  setTimeout(doPoll, 5000);
});
