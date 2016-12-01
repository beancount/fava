import Awesomplete from 'awesomplete';

import { $, $$, handleJSON } from './helpers';
import e from './events';

function submitTransactionForm(successCallback) {
  const jsonData = {
    date: $('input[name="date"]').value,
    payee: $('input[name="payee"]').value,
    description: $('input[name="description"]').value,
    postings: [],
  };

  $$('.posting').forEach((posting) => {
    const account = posting.querySelector('input[name="account"]').value;
    const value = posting.querySelector('input[name="value"]').value;
    const currency = posting.querySelector('select[name="currency"]').value;

    if (account) {
      jsonData.postings.push({
        account,
        value,
        currency: value ? currency : '',
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
  const payeeInput = $('#transaction-form input[name="payee"]');

  const payeeOptions = {
    autoFirst: true,
    minChars: 0,
    maxItems: 30,
    filter(text, input) {
      return Awesomplete.FILTER_CONTAINS(text, input.match(/[^,]*$/)[0]); // eslint-disable-line new-cap, max-len
    },
  };
  const payeeCompleter = new Awesomplete(payeeInput, payeeOptions);

  payeeInput.addEventListener('focus', () => {
    payeeCompleter.evaluate();
  });

  $$('input[name="account"]').forEach((inputEl) => {
    const accountOptions = {
      autoFirst: true,
      minChars: 0,
      maxItems: 30,
      filter(text, input) {
        return Awesomplete.FILTER_CONTAINS(text, input.match(/[^,]*$/)[0]); // eslint-disable-line new-cap, max-len
      },
    };
    const accountCompleter = new Awesomplete(inputEl, accountOptions);

    inputEl.addEventListener('focus', () => {
      accountCompleter.evaluate();
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
