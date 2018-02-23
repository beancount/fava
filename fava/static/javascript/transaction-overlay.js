import e from './events';
import EntryForm from './entry-forms';
import { closeOverlay } from './overlays';

e.on('button-click-transaction-form-submit', (button) => {
  const form = new EntryForm(button.form.querySelector('.entry-form'));
  EntryForm.submit([form], () => {
    form.reset();
    closeOverlay();
  });
});

e.on('button-click-transaction-form-submit-and-new', (button) => {
  const form = new EntryForm(button.form.querySelector('.entry-form'));
  EntryForm.submit([form], () => {
    form.reset();
  });
});
