import { $, $$, handleJSON } from './helpers';
import e from './events';

function submitIngestForm() {
  const form = $('.ingest-extract');
  const jsonData = { entries: [] };

  form.querySelectorAll('.ingest-row.import .entry-form.transaction').forEach((transaction) => {
    const transactionData = {
      date: transaction.querySelector('input[name=date]').value,
      flag: transaction.querySelector('input[name=flag]').value,
      payee: transaction.querySelector('input[name=payee]').value,
      narration: transaction.querySelector('input[name=narration]').value,
      metadata: {},
      postings: [],
      type: 'transaction',
    };

    transaction.querySelectorAll('.posting').forEach((posting) => {
      const account = posting.querySelector('input[name=account]').value;
      const number = posting.querySelector('input[name=number]').value;
      const currency = posting.querySelector('input[name=currency]').value;

      if (account) {
        transactionData.postings.push({
          account,
          number,
          currency: number ? currency : '',
        });
      }
    });

    jsonData.entries.push(transactionData);
  });

  form.querySelectorAll('.ingest-row.import .entry-form.balance').forEach((balance) => {
    const balanceData = {
      date: balance.querySelector('input[name=date]').value,
      account: balance.querySelector('input[name=account]').value,
      number: balance.querySelector('input[name=number]').value,
      currency: balance.querySelector('input[name=currency]').value,
      metadata: {},
      type: 'balance',
    };

    jsonData.entries.push(balanceData);
  });

  form.querySelectorAll('.ingest-row.import .entry-form.note').forEach((balance) => {
    const noteData = {
      date: balance.querySelector('input[name=date]').value,
      account: balance.querySelector('input[name=account]').value,
      comment: balance.querySelector('textarea[name=comment]').value,
      metadata: {},
      type: 'note',
    };

    jsonData.entries.push(noteData);
  });

  $.fetch(form.getAttribute('action'), {
    method: 'PUT',
    body: JSON.stringify(jsonData),
    headers: { 'Content-Type': 'application/json' },
  })
    .then(handleJSON)
    .then((data) => {
      e.trigger('reload');
      e.trigger('info', data.message);
    }, (error) => {
      e.trigger('error', `Importing failed: ${error}`);
    });
}

function initExtract() {
  const ingest = $('.ingest-extract');
  if (!ingest) return;

  $.delegate(ingest, 'click', '.actions input', (event) => {
    const input = event.target;
    input.closest('.ingest-row').className = `ingest-row ${input.value}`;
  });

  ingest.querySelector('.ingest-form-submit').addEventListener('click', (event) => {
    event.preventDefault();
    submitIngestForm();
  });

  $('#toggle-ignore').addEventListener('click', (event) => {
    const value = event.target.classList.contains('inactive') ? 'import' : 'ignore';
    $$(`.ingest-row input[value=${value}]`).forEach((input) => {
      input.click();
    });
    event.target.classList.toggle('inactive');
  });

  $('#toggle-source').addEventListener('click', () => {
    $$('.ingest-row .source').forEach((element) => {
      element.classList.toggle('hidden');
    });
    event.target.classList.toggle('inactive');
  });
}

export default function initIngest() {
  initExtract();
}
