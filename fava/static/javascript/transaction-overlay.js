import e from './events';
import { $, $$, handleJSON } from './helpers';
import { addPostingRow, entryFormToJSON } from './entry-forms';
import { closeOverlay } from './overlays';

function submitTransactionForm(form, successCallback) {
  const jsonData = {
    entries: [
      entryFormToJSON(form.querySelector('.entry-form')),
    ],
  };

  $.fetch(form.getAttribute('action'), {
    method: 'PUT',
    body: JSON.stringify(jsonData),
    headers: { 'Content-Type': 'application/json' },
  })
    .then(handleJSON)
    .then((data) => {
      $$('.metadata', form).forEach((el) => {
        el.remove();
      });
      $$('.posting', form).forEach((el) => {
        el.remove();
      });
      addPostingRow(form);
      addPostingRow(form);
      form.focus();
      e.trigger('reload');
      e.trigger('info', data.message);
      if (successCallback) {
        successCallback();
      }
    }, (error) => {
      e.trigger('error', `Adding transaction failed: ${error}`);
    });
}

let initialized = false;
export default function showTransactionOverlay() {
  const form = $('#transaction-form');
  if (!initialized) {
    addPostingRow(form);
    addPostingRow(form);
    initialized = true;
  }
  $('#transaction').classList.add('shown');
  form.focus();
}

e.on('page-init', () => {
  const form = $('#transaction #transaction-form');

  form.querySelector('#transaction-form-submit').addEventListener('click', () => {
    submitTransactionForm(form, closeOverlay);
  });

  form.querySelector('#transaction-form-submit-and-new').addEventListener('click', () => {
    submitTransactionForm(form);
  });
});
