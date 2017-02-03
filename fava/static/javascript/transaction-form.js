import Awesomplete from 'awesomplete';
import fuzzy from 'fuzzyjs';

import { $, $$, handleJSON } from './helpers';
import e from './events';

function initInput(input) {
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

function addPostingRow() {
  const newPosting = $('#posting-template').cloneNode(true);
  newPosting.querySelectorAll('input').forEach((input) => {
    initInput(input);
  });
  $('#transaction-form .postings').appendChild(newPosting);
  newPosting.setAttribute('id', '');
  return newPosting;
}

function addMetadataRow() {
  const newMetadata = $('#metadata-template').cloneNode(true);
  newMetadata.querySelectorAll('input').forEach((input) => {
    initInput(input);
  });
  $('#transaction-form .metadatas').appendChild(newMetadata);
  newMetadata.setAttribute('id', '');
  return newMetadata;
}

function submitTransactionForm(successCallback) {
  const jsonData = {
    date: $('#transaction-form input[name=date]').value,
    flag: $('#transaction-form input[name=flag]').value,
    payee: $('#transaction-form input[name=payee]').value,
    narration: $('#transaction-form input[name=narration]').value,
    metadata: {},
    postings: [],
  };

  $$('#transaction-form .metadata').forEach((metadata) => {
    const key = metadata.querySelector('input[name=metadata-key]').value;
    const value = metadata.querySelector('input[name=metadata-value]').value;

    if (key) {
      jsonData.metadata[key] = value;
    }
  });

  $$('#transaction-form .posting').forEach((posting) => {
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

  const form = $('#transaction-form');
  $.fetch(form.getAttribute('action'), {
    method: 'PUT',
    body: JSON.stringify(jsonData),
    headers: { 'Content-Type': 'application/json' },
  })
    .then(handleJSON)
    .then((data) => {
      $$('#transaction-form .metadata').forEach((el) => {
        el.remove();
      });
      $$('#transaction-form .posting').forEach((el) => {
        el.remove();
      });
      addPostingRow();
      addPostingRow();
      $('input[name="date"]').focus();
      e.trigger('reload');
      e.trigger('info', data.message);
      if (successCallback) {
        successCallback();
      }
    }, (error) => {
      e.trigger('error', `Adding transcation failed: ${error}`);
    });
}

export default function initTransactionForm() {
  let initialized = false;

  $('#add-transaction-button').addEventListener('click', () => {
    if (!initialized) {
      $$('#transaction-form input').forEach((input) => {
        initInput(input);
      });
      addPostingRow();
      addPostingRow();
      initialized = true;
    }
    $('#transaction').classList.add('shown');
    $('input[name="date"]').focus();
  });

  $('#transaction-form-submit').addEventListener('click', (event) => {
    event.preventDefault();
    submitTransactionForm(() => {
      $('.transaction-form').classList.remove('shown');
    });
  });

  $('#transaction-form-submit-and-new').addEventListener('click', (event) => {
    event.preventDefault();
    submitTransactionForm();
  });

  $.delegate($('#transaction-form'), 'click', '.add-posting', (event) => {
    event.preventDefault();
    const newPosting = addPostingRow();
    newPosting.querySelector('.account').focus();
  });

  $('#add-metadata').addEventListener('click', (event) => {
    event.preventDefault();
    const newMetadata = addMetadataRow();
    newMetadata.querySelector('.metadata-key').focus();
  });

  $.delegate($('#transaction-form'), 'click', '.add-metadata', (event) => {
    event.preventDefault();
    const newMetadata = addMetadataRow();
    newMetadata.querySelector('.metadata-key').focus();
  });
}
