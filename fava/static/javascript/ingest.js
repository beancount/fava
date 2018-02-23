import { $, $$ } from './helpers';
import EntryForm from './entry-forms';
import e from './events';

e.on('button-click-extract-submit', () => {
  const form = $('.ingest-extract');
  const forms = $$('.ingest-row.import .entry-form', form).map(el => new EntryForm(el));
  EntryForm.submit(forms);
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
