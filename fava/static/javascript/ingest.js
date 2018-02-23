import { $, $$, handleJSON } from './helpers';
import EntryForm from './entry-forms';
import e from './events';

e.on('button-click-extract-submit', (button) => {
  const url = button.getAttribute('data-url');
  const form = $('.ingest-extract');
  const jsonData = { entries: [] };

  let allValid = true;

  $$('.ingest-row.import .entry-form', form).forEach((entryForm) => {
    try {
      jsonData.entries.push(new EntryForm(entryForm).toJSON());
    } catch (error) {
      allValid = false;
    }
  });

  if (!allValid) return;

  $.fetch(url, {
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
});

e.on('button-click-extract-toggle-ignore', (button) => {
  const toImport = button.classList.contains('inactive');
  const value = toImport ? 'import' : 'ignore';
  $$(`.ingest-row.${toImport ? 'ignore' : 'import'} input[value=${value}]`).forEach((input) => {
    input.click();
  });
  button.classList.toggle('inactive');
});

e.on('button-click-extract-toggle-source', (button) => {
  $$('.ingest-row .source').forEach((element) => {
    element.classList.toggle('hidden');
  });
  button.classList.toggle('inactive');
});

e.on('page-loaded', () => {
  const ingest = $('.ingest-extract');
  if (!ingest) return;

  $.delegate(ingest, 'click', '.actions input', (event) => {
    const input = event.target;
    input.closest('.ingest-row').className = `ingest-row ${input.value}`;
  });
});
