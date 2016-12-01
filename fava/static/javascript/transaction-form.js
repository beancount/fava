import Awesomplete from 'awesomplete';
import fuzzy from 'fuzzyjs';

import { $, $$, handleJSON } from './helpers';
import e from './events';

function submitTransactionForm(successCallback) {
  const jsonData = {
    date: $('input[name="date"]').value,
    flag: $('input[name="flag"]').value,
    payee: $('input[name="payee"]').value,
    narration: $('input[name="narration"]').value,
    postings: [],
  };

  $$('.posting').forEach((posting) => {
    const account = posting.querySelector('input[name="account"]').value;
    const number = posting.querySelector('input[name="number"]').value;
    const currency = posting.querySelector('select[name="currency"]').value;

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
      form.reset();
      e.trigger('reload');
      e.trigger('info', data.message);
      if (successCallback) {
        successCallback();
      }
    }, (error) => {
      e.trigger('error', `Save error: ${error}`);
    });
}

export default function initTransactionForm() {
  $$('#transaction-form input').forEach((input) => {
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
}
