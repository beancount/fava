import { $, $$ } from './helpers';
import e from './events';

import initSourceEditor from './editor';
import showTransactionOverlay from './transaction-overlay';

export function closeOverlay() {
  $('#context-overlay .content').innerHTML = '';
  $$('.overlay-wrapper').forEach((el) => {
    el.classList.remove('shown');
  });
  window.location.hash = '';
}

// Show various overlays depending on the hash.
export function handleHash() {
  const hash = window.location.hash;
  if (!hash) {
    closeOverlay();
  } else if (hash === '#add-transaction') {
    showTransactionOverlay();
  } else if (hash.startsWith('#context')) {
    $.fetch(`${window.favaAPI.baseURL}_context/?entry_hash=${hash.slice(9)}`)
      .then(response => response.text())
      .then((data) => {
        $('#context-overlay .content').innerHTML = data;
        initSourceEditor('#source-slice-editor');
      }, () => {
        e.trigger('error', 'Loading context failed.');
      });
    $('#context-overlay').classList.add('shown');
  }
}

e.on('page-init', () => {
  $$('.overlay-wrapper').forEach((el) => {
    el.addEventListener('mousedown', (event) => {
      if (event.target.classList.contains('overlay-wrapper') ||
          event.target.classList.contains('close-overlay')) {
        closeOverlay();
      }
    });
  });
  $.delegate($('#context-overlay'), 'click', '.toggle-box-header', (event) => {
    event.target.closest('.toggle-box').classList.toggle('toggled');
  });
});

