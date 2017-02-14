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

function addPostingRow(form) {
  const newPosting = $('#posting-template').cloneNode(true);
  newPosting.querySelectorAll('input').forEach((input) => {
    initInput(input);
  });
  form.querySelector('.postings').appendChild(newPosting);
  newPosting.setAttribute('id', '');
  return newPosting;
}

function addMetadataRow(form) {
  const newMetadata = $('#metadata-template').cloneNode(true);
  newMetadata.querySelectorAll('input').forEach((input) => {
    initInput(input);
  });
  form.querySelectorAll('.metadatas').appendChild(newMetadata);
  newMetadata.setAttribute('id', '');
  return newMetadata;
}

function submitTransactionForm(form, successCallback) {
  const jsonData = {
    date: form.querySelector('input[name=date]').value,
    flag: form.querySelector('input[name=flag]').value,
    payee: form.querySelector('input[name=payee]').value,
    narration: form.querySelector('input[name=narration]').value,
    metadata: {},
    postings: [],
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

  $.fetch(form.parentNode.getAttribute('action'), {
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

function initTransactionOverlay() {
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

export default function initTransactionForms() {
  initTransactionOverlay();
  $$('.transaction-form').forEach((el) => {
    initTransactionForm(el);
  });
}
