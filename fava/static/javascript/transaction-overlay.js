import { $ } from './helpers';
import { initInput, addPostingRow, addMetadataRow, submitTransactionForm } from './entry-forms';

export default function initTransactionOverlay() {
  const form = $('#transaction #transaction-form');
  let initialized = false;

  // TODO
  $('#add-transaction-button').addEventListener('click', () => {
    if (!initialized) {
      form.querySelectorAll('input').forEach((input) => {
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
      // TODO
      form.querySelector('.transaction-form').classList.remove('shown');
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
