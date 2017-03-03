import Awesomplete from 'awesomplete';
import fuzzy from 'fuzzyjs';

import { $, $$, handleJSON } from './helpers';
import e from './events';

export function initInput(input) {
  if (!input.getAttribute('list')) {
    return;
  }

  const options = {
    autoFirst: true,
    minChars: 0,
    maxItems: 30,
    filter(suggestion, search) {
      return fuzzy.test(search, suggestion.value);
    },
  };
  const completer = new Awesomplete(input, options);

  input.addEventListener('focus', () => {
    completer.evaluate();
  });
}

export function addPostingRow(form) {
  const newPosting = $('#posting-template').cloneNode(true);
  newPosting.querySelectorAll('input').forEach((input) => {
    initInput(input);
  });
  form.querySelector('.postings').appendChild(newPosting);
  newPosting.setAttribute('id', '');
  return newPosting;
}

export function addMetadataRow(form) {
  const newMetadata = $('#metadata-template').cloneNode(true);
  newMetadata.querySelectorAll('input').forEach((input) => {
    initInput(input);
  });
  form.querySelectorAll('.metadatas').appendChild(newMetadata);
  newMetadata.setAttribute('id', '');
  return newMetadata;
}

export function submitTransactionForm(form, successCallback) {
  const jsonData = {
    date: form.querySelector('input[name=date]').value,
    flag: form.querySelector('input[name=flag]').value,
    payee: form.querySelector('input[name=payee]').value,
    narration: form.querySelector('input[name=narration]').value,
    metadata: {},
    postings: [],
    type: 'transaction',
  };

  form.querySelectorAll('.metadata').forEach((metadata) => {
    const key = metadata.querySelector('input[name=metadata-key]').value;
    const value = metadata.querySelector('input[name=metadata-value]').value;

    if (key) {
      jsonData.metadata[key] = value;
    }
  });

  form.querySelectorAll('.posting').forEach((posting) => {
    const account = posting.querySelector('input[name=account]').value;
    const number = posting.querySelector('input[name=number]').value;
    const currency = posting.querySelector('input[name=currency]').value;

    if (account) {
      jsonData.postings.push({
        account,
        number,
        currency: number ? currency : '',
      });
    }
  });

  $.fetch(form.getAttribute('action'), {
    method: 'PUT',
    body: JSON.stringify(jsonData),
    headers: { 'Content-Type': 'application/json' },
  })
    .then(handleJSON)
    .then((data) => {
      form.querySelectorAll('.metadata').forEach((el) => {
        el.remove();
      });
      form.querySelectorAll('.posting').forEach((el) => {
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
      e.trigger('error', `Adding transcation failed: ${error}`);
    });
}

function initTransactionForm(form) {
  form.querySelectorAll('input').forEach((input) => {
    initInput(input);
  });

  $.delegate(form, 'click', '.add-posting', (event) => {
    event.preventDefault();
    const newPosting = addPostingRow(form);
    newPosting.querySelector('.account').focus();
  });

  $.delegate(form, 'click', '.add-metadata', (event) => {
    event.preventDefault();
    const newMetadata = addMetadataRow(form);
    newMetadata.querySelector('.metadata-key').focus();
  });
}

function initBalanceForm(form) {
  form.querySelectorAll('input').forEach((input) => {
    initInput(input);
  });
}

function initNoteForm(form) {
  form.querySelectorAll('input').forEach((input) => {
    initInput(input);
  });
}

export default function initEntryForms() {
  $$('.transaction-form').forEach((el) => {
    initTransactionForm(el);
  });

  $$('.balance-form').forEach((el) => {
    initBalanceForm(el);
  });

  $$('.note-form').forEach((el) => {
    initNoteForm(el);
  });
}
