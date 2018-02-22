import e from './events';
import { $, handleJSON } from './helpers';
import EntryForm from './entry-forms';
import { closeOverlay } from './overlays';

function submitTransactionForm(form, successCallback) {
  const entryForm = new EntryForm(form.querySelector('.entry-form'));
  const jsonData = {
    entries: [
      entryForm.toJSON(),
    ],
  };

  $.fetch(form.getAttribute('action'), {
    method: 'PUT',
    body: JSON.stringify(jsonData),
    headers: { 'Content-Type': 'application/json' },
  })
    .then(handleJSON)
    .then((data) => {
      entryForm.reset();
      e.trigger('reload');
      e.trigger('info', data.message);
      if (successCallback) {
        successCallback();
      }
    }, (error) => {
      e.trigger('error', `Adding transaction failed: ${error}`);
    });
}

e.on('button-click-transaction-form-submit', (button) => {
  submitTransactionForm(button.form, closeOverlay);
});

e.on('button-click-transaction-form-submit-and-new', (button) => {
  submitTransactionForm(button.form);
});
