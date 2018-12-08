import e from './events';
import EntryForm from './entry-forms';

e.on('button-click-transaction-form-submit', button => {
  const form = new EntryForm(button.form.querySelector('.entry-form'));
  EntryForm.submit([form], () => {
    form.reset();
    e.trigger('close-overlay');
  });
});

e.on('button-click-transaction-form-submit-and-new', button => {
  const form = new EntryForm(button.form.querySelector('.entry-form'));
  EntryForm.submit([form], () => {
    form.reset();
  });
});
