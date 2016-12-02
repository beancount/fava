import Awesomplete from 'awesomplete';
import fuzzy from 'fuzzyjs';

import { $, $$, handleJSON } from './helpers';
import e from './events';

function submitTransactionForm(successCallback) {
  const jsonData = {
    date: $('#transaction-form input[name=date]').value,
    flag: $('#transaction-form input[name=flag]').value,
    payee: $('#transaction-form input[name=payee]').value,
    narration: $('#transaction-form input[name=narration]').value,
    postings: [],
  };

  $$('.posting').forEach((posting) => {
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
      form.reset();
      $$('#transaction-form .posting').forEach((el, index) => {
        if (index > 1) {
          el.remove();
        }
      });
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

  $.delegate($('#transaction-form'), 'click', '.add-posting', (event) => {
    event.preventDefault();
    const newPosting = $('#transaction-form .posting').cloneNode(true);
    newPosting.querySelectorAll('input').forEach((element) => {
      element.value = ''; // eslint-disable-line no-param-reassign
    });
    $('#transaction-form .postings').appendChild(newPosting);
    newPosting.querySelector('.account').focus();
  });
}
