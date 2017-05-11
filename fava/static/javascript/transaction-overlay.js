import e from './events';
import { $, $$, handleJSON } from './helpers';
import { initInput, addPostingRow, addMetadataRow, entryFormToJSON } from './entry-forms';

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
      form.querySelector('input[name="date"]').focus();
      e.trigger('reload');
      e.trigger('info', data.message);
      if (successCallback) {
        successCallback();
      }
    }, (error) => {
      e.trigger('error', `Adding transaction failed: ${error}`);
    });
}

export default function initTransactionOverlay() {
  const form = $('#transaction #transaction-form');
  let initialized = false;

  $('#add-transaction-button').addEventListener('click', () => {
    if (!initialized) {
      $$('input', form).forEach((input) => {
        initInput(input);
      });
      addPostingRow(form);
      addPostingRow(form);
      initialized = true;
    }
    $('#transaction').classList.add('shown');
    form.querySelector('input[name="date"]').focus();
  });

  form.querySelector('#transaction-form-submit').addEventListener('click', (event) => {
    event.preventDefault();
    submitTransactionForm(form, () => {
      $('#transaction').classList.remove('shown');
    });
  });

  form.querySelector('#transaction-form-submit-and-new').addEventListener('click', (event) => {
    event.preventDefault();
    submitTransactionForm(form);
  });

  form.querySelector('#add-metadata').addEventListener('click', (event) => {
    event.preventDefault();
    const newMetadata = addMetadataRow(form);
    newMetadata.querySelector('.metadata-key').focus();
  });
}
