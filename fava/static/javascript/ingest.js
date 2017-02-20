import { $, $$, handleJSON } from './helpers';
import e from './events';

function initRow(row) {
  row.querySelectorAll('.action input').forEach((el) => {
    el.addEventListener('click', () => {
      row.className = `ingest-row ${el.value}`; // eslint-disable-line no-param-reassign
    });
  });
}

function submitIngestForm() {
  const form = $('.ingest-extract');
  const jsonData = { entries: [] };

  form.querySelectorAll('.ingest-row.import .transaction-form').forEach((transaction) => {
    const transactionData = {
      date: transaction.querySelector('input[name=date]').value,
      flag: transaction.querySelector('input[name=flag]').value,
      payee: transaction.querySelector('input[name=payee]').value,
      narration: transaction.querySelector('input[name=narration]').value,
      metadata: {},
      postings: [],
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

function initIdentify() {
  const files = $$('.ingest-files button');
  if (!files) return;

  files.forEach((button) => {
    button.addEventListener('click', (event) => {
      event.preventDefault();
      window.location = button.getAttribute('href');
    });
  });
}

function initExtract() {
  const ingest = $('.ingest-extract');
  if (!ingest) return;

  $$('.ingest-row').forEach((row) => {
    initRow(row);
  });

  ingest.querySelector('.ingest-form-submit').addEventListener('click', (event) => {
    event.preventDefault();
    submitIngestForm();
  });
}

export default function initIngest() {
  initIdentify();
  initExtract();
}
