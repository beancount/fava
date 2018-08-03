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
// close-overlay:
//    Close any open overlays.
//
// button-click-*:
//    For <button>s that have a `data-event` attribute, the event
//    `button-click-${data-event}` will be triggered.
//

import { $, handleJSON } from './helpers';
import e from './events';
import router from './router';

import './autocomplete';
import './charts';
import './clipboard';
import './documents-upload';
import './editor';
import './entry-forms';
import './filters';
import './ingest';
import './journal';
import './keyboard-shortcuts';
import './notifications';
import './overlays';
import './sidebar';
import './sort';
import './transaction-overlay';
import './tree-table';

e.on('page-loaded', () => {
  window.favaAPI = JSON.parse($('#ledger-data').innerHTML);
  document.title = $('#data-document-title').value;
  $('h1 strong').innerHTML = $('#data-page-title').innerHTML;
  $('#reload-page').classList.add('hidden');
});

e.on('page-init', () => {
  // Watch for all clicks on <button>s and fire the appropriate events.
  $.delegate(document.body, 'click', 'button', (event) => {
    const button = event.target.closest('button');
    const type = button.getAttribute('data-event');
    if (type) {
      e.trigger(`button-click-${type}`, button);
    }
  });

  // Watch for all submits of <forms>s and fire the appropriate events.
  $.delegate(document.body, 'submit', 'form', (event) => {
    const form = event.target;
    const type = form.getAttribute('data-event');
    if (type) {
      event.preventDefault();
      e.trigger(`form-submit-${type}`, form);
    }
  });
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
          e.trigger('reload-warning', $('#reload-page').getAttribute('data-reload-text'));
        }
      }
    }, () => {})
    .then(() => {
      setTimeout(doPoll, 5000);
    });
}

$.ready().then(() => {
  window.favaAPI = JSON.parse($('#ledger-data').innerHTML);
  router.init();
  e.trigger('page-init');
  e.trigger('page-loaded');
  setTimeout(doPoll, 5000);
});
