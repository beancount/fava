import e from './events';
import { $, $$, handleJSON } from './helpers';

// Various helpers to deal with entry forms.
export default class EntryForm {
  constructor(form) {
    this.form = form;
    this.type = this.form.getAttribute('data-type');
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
    $('[name=payee]', this.form).value = '';
    $$('.metadata-row', this.form).forEach(el => {
      el.remove();
    });
    $$('.posting', this.form).forEach(el => {
      el.remove();
    });
    this.addPosting();
    this.addPosting();
    this.form.focus();
  }

  // Check validity of the form.
  checkValidity() {
    if ($$('input', this.form).some(input => !input.checkValidity()))
      return false;
    if (this.type === 'Transaction' && $$('.posting', this.form).length === 0)
      return false;
    return true;
  }

  // Convert the form data to JSON.
  toJSON() {
    if (!this.checkValidity()) throw new Error();

    const entryData = {
      type: this.type,
      meta: {},
    };

    $$('[name]', this.form).forEach(input => {
      entryData[input.name] = input.value;
    });

    $$('.metadata-row', this.form).forEach(row => {
      const key = row.querySelector('.metadata-key').value;
      entryData.meta[key] = row.querySelector('.metadata-value').value;
    });

    if (this.type === 'Transaction') {
      entryData.postings = [];
      $$('.posting', this.form).forEach(posting => {
        entryData.postings.push({
          account: posting.querySelector('.account').value,
          amount: posting.querySelector('.amount').value,
        });
      });
    }

    if (this.type === 'Balance') {
      entryData.account = this.form.querySelector('.account').value;
    }

    return entryData;
  }

  // Check if the form is empty (but for date and payee).
  isEmpty() {
    let empty = true;
    if ($('[name=narration]', this.form).value) empty = false;
    $$('.posting', this.form).forEach(posting => {
      if (posting.querySelector('.account').value) empty = false;
    });
    return empty;
  }

  // Set all but date and payee like in the given transaction (if empty).
  set(entry) {
    if (!this.isEmpty()) return;
    $('[name=narration]', this.form).value = entry.narration;
    $$('.posting', this.form).forEach(el => {
      el.remove();
    });
    entry.postings.forEach(posting => {
      const { account, amount } = posting;
      const row = this.addPosting();
      $('.account', row).value = account;
      if (amount) {
        $('.amount', row).value = amount;
      }
    });
  }

  // Submit an Array of forms (do nothing if one of them is invalid).
  static submit(forms, successCallback) {
    const jsonData = { entries: [] };
    let allValid = true;

    forms.forEach(entryForm => {
      try {
        jsonData.entries.push(entryForm.toJSON());
      } catch (error) {
        allValid = false;
      }
    });

    if (!allValid) return;

    $.fetch(`${window.favaAPI.baseURL}api/add-entries/`, {
      method: 'PUT',
      body: JSON.stringify(jsonData),
      headers: { 'Content-Type': 'application/json' },
    })
      .then(handleJSON)
      .then(
        data => {
          e.trigger('reload');
          e.trigger('info', data.message);
          if (successCallback) {
            successCallback();
          }
        },
        error => {
          e.trigger('error', `Saving failed: ${error}`);
        },
      );
  }
}

e.on('button-click-remove-fieldset', button => {
  button.closest('.fieldset').remove();
});

e.on('button-click-add-metadata', button => {
  new EntryForm(button.closest('.entry-form'))
    .addMetadata()
    .querySelector('input')
    .focus();
});

e.on('button-click-add-posting', button => {
  new EntryForm(button.closest('.entry-form'))
    .addPosting()
    .querySelector('input')
    .focus();
});

// Autofill complete transactions.
e.on('autocomplete-select-payees', input => {
  const payee = input.value;
  const params = new URLSearchParams();
  params.set('payee', payee);
  $.fetch(
    `${window.favaAPI.baseURL}api/payee-transaction/?${params.toString()}`,
  )
    .then(handleJSON)
    .then(data => data.payload)
    .then(entry => {
      const form = input.closest('.entry-form');
      if (!form || !entry) return;
      new EntryForm(form).set(entry);
    });
});
