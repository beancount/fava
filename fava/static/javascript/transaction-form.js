import Awesomplete from 'awesomplete';

import { $, $$, handleJSON } from './helpers';
import e from './events';

function submitTransactionForm(successCallback) {
  let jsonData = {
    date: $('input[name="date"]').value,
    payee: $('input[name="payee"]').value,
    description: $('input[name="description"]').value,
    postings: []
  };

  $$('.posting').forEach((posting) => {
    const account = posting.querySelector('input[name="account"]').value;
    const value = posting.querySelector('input[name="value"]').value;
    const currency = posting.querySelector('select[name="currency"]').value;

    if (account) {
      jsonData.postings.push({
        account,
        value,
        currency: value ? currency : ''
      });
    }
  });

  const form = $('#transaction-form');
  $.fetch(form.getAttribute('action'), {
    method: 'PUT',
    body: JSON.stringify(jsonData),
    headers: { 'Content-Type': 'application/json' }
  })
    .then(handleJSON)
    .then((data) => {
      form.reset();
      e.trigger('reload');
      e.trigger('info', data.message);
      successCallback && successCallback();
    }, (error) => {
      e.trigger('error', `Save error: ${error}`);
    });
}

export default function initTransactionForm() {
  const payeeInput = $('#transaction-form input[name="payee"]');

  let options = {
    autoFirst: true,
    minChars: 0,
    maxItems: 30,
    filter(text, input) {
      return Awesomplete.FILTER_CONTAINS(text, input.match(/[^,]*$/)[0]); // eslint-disable-line new-cap, max-len
    }
  };
  const completer = new Awesomplete(payeeInput, options);

  payeeInput.addEventListener('focus', () => {
    completer.evaluate();
  });

  $$('input[name="account"]').forEach((input) => {
    let options = {
      autoFirst: true,
      minChars: 0,
      maxItems: 30,
      filter(text, input) {
        return Awesomplete.FILTER_CONTAINS(text, input.match(/[^,]*$/)[0]); // eslint-disable-line new-cap, max-len
      }
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
