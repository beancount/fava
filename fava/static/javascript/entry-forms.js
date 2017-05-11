import Awesomplete from 'awesomplete';
import fuzzy from 'fuzzyjs';

import { $, $$, handleJSON } from './helpers';

// These will be updated once a payee is set.
const accountCompleters = [];

function updateAccountCompleters(payee) {
  $.fetch(`${window.favaAPI.baseURL}api/payee-accounts/?payee=${payee}`)
    .then(handleJSON)
    .then((data) => {
      accountCompleters.forEach((completer) => {
        completer.list = data.payload; // eslint-disable-line no-param-reassign
      });
    });
}

export function initInput(input) {
  const listAttribute = input.getAttribute('list');
  if (!listAttribute) {
    return;
  }

  const options = {
    autoFirst: true,
    minChars: 0,
    maxItems: 30,
    filter(suggestion, search) {
      return fuzzy.test(search, suggestion.value);
    },
    sort: false,
  };
  const completer = new Awesomplete(input, options);

  if (listAttribute === 'accounts') {
    accountCompleters.push(completer);
  }

  if (listAttribute === 'payees') {
    input.addEventListener('blur', () => {
      updateAccountCompleters(input.value);
    });
  }

  input.addEventListener('focus', () => {
    completer.evaluate();
  });
}

export function addPostingRow(form) {
  const newPosting = $('#posting-template').cloneNode(true);
  $$('input', newPosting).forEach((input) => {
    initInput(input);
  });
  form.querySelector('.postings').appendChild(newPosting);
  newPosting.setAttribute('id', '');
  return newPosting;
}

export function addMetadataRow(form) {
  const newMetadata = $('#metadata-template').cloneNode(true);
  $$('input', newMetadata).forEach((input) => {
    initInput(input);
  });
  form.querySelector('.metadata').appendChild(newMetadata);
  newMetadata.setAttribute('id', '');
  return newMetadata;
}

export function entryFormToJSON(form) {
  const entryData = {};
  entryData.type = form.getAttribute('data-type');

  $$('input', form.querySelector('.fieldset')).forEach((input) => {
    entryData[input.name] = input.value;
  });

  entryData.metadata = {};
  $$('.metadata-row', form).forEach((metadata) => {
    const key = metadata.querySelector('input[name=metadata-key]').value;
    if (key) {
      entryData.metadata[key] = metadata.querySelector('input[name=metadata-value]').value;
    }
  });

  if (entryData.type === 'transaction') {
    entryData.postings = [];
    $$('.posting', form).forEach((posting) => {
      const account = posting.querySelector('input[name=account]').value;

      if (account) {
        entryData.postings.push({
          account,
          number: posting.querySelector('input[name=number]').value,
          currency: posting.querySelector('input[name=currency]').value,
        });
      }
    });
  }

  return entryData;
}

export default function initEntryForms() {
  $$('.entry-form').forEach((form) => {
    $$('input', form).forEach((input) => {
      initInput(input);
    });

    if (form.classList.contains('transaction')) {
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
  });
}
