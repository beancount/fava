import e from './events';
import { formatCurrency } from './format';
import { $, $$, handleJSON } from './helpers';

// Various helpers to deal with entry forms.
export default class EntryForm {
  constructor(form) {
    this.form = form;
  }

  // Append a posting row.
  addPosting() {
    const newPosting = $('#posting-template').children[0].cloneNode(true);
    this.form.querySelector('.postings').appendChild(newPosting);
    return newPosting;
  }

  // Append a metadata row.
  addMetadata() {
    const newMetadata = $('#metadata-template').children[0].cloneNode(true);
    this.form.querySelector('.metadata').appendChild(newMetadata);
    return newMetadata;
  }

  // Reset the entry form.
  reset() {
    $('[name=narration]', this.form).value = '';
    $$('.metadata', this.form).forEach((el) => { el.remove(); });
    $$('.posting', this.form).forEach((el) => { el.remove(); });
    this.addPosting();
    this.addPosting();
    this.form.focus();
  }

  // Convert the form data to JSON.
  toJSON() {
    const entryData = {
      type: this.form.getAttribute('data-type'),
      metadata: {},
    };

    $$('[name]', this.form).forEach((input) => {
      entryData[input.name] = input.value;
    });

    $$('.metadata-row', this.form).forEach((metadata) => {
      const key = metadata.querySelector('.metadata-key').value;
      if (key) {
        entryData.metadata[key] = metadata.querySelector('.metadata-value').value;
      }
    });

    if (entryData.type === 'Transaction') {
      entryData.postings = [];
      $$('.posting', this.form).forEach((posting) => {
        const account = posting.querySelector('.account').value;

        if (account) {
          entryData.postings.push({
            account,
            number: posting.querySelector('.number').value,
            currency: posting.querySelector('.currency').value,
          });
        }
      });
    }

    return entryData;
  }

  // Check if the form is empty (but for date and payee).
  isEmpty() {
    let empty = true;
    if ($('[name=narration]', this.form).value) empty = false;
    $$('.posting', this.form).forEach((posting) => {
      if (posting.querySelector('.account').value) empty = false;
    });
    return empty;
  }

  // Set all but date and payee like in the given transaction (if empty).
  set(entry) {
    if (!this.isEmpty()) return;
    $('[name=narration]', this.form).value = entry.narration;
    $$('.posting', this.form).forEach((el) => { el.remove(); });
    entry.postings.forEach((posting) => {
      const { account, units } = posting;
      const row = this.addPosting();
      $('.account', row).value = account;
      if (units) {
        const [number, currency] = units;
        $('.number', row).value = formatCurrency(number);
        $('.currency', row).value = currency;
      }
    });
  }
}

e.on('button-click-remove-fieldset', (button) => {
  button.closest('.fieldset').remove();
});

e.on('button-click-add-metadata', (button) => {
  new EntryForm(button.closest('.entry-form'))
    .addMetadata()
    .querySelector('input')
    .focus();
});

e.on('button-click-add-posting', (button) => {
  new EntryForm(button.closest('.entry-form'))
    .addPosting()
    .querySelector('input')
    .focus();
});

// Autofill complete transactions.
e.on('autocomplete-select-payees', (input) => {
  const payee = input.value;
  $.fetch(`${window.favaAPI.baseURL}api/payee-transaction/?payee=${payee}`)
    .then(handleJSON)
    .then(data => data.payload)
    .then((entry) => {
      const form = input.closest('.entry-form');
      if (!form || !entry) return;
      new EntryForm(form).set(entry);
    });
});
