import e from './events';
import { $, handleJSON } from './helpers';
import { resetEntryForm, entryFormToJSON } from './entry-forms';
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
      resetEntryForm(form);
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
