import { $, $$, handleJSON } from './helpers';
import { entryFormToJSON } from './entry-forms';
import e from './events';

function submitIngestForm() {
  const form = $('.ingest-extract');
  const jsonData = { entries: [] };

  $$('.ingest-row.import .entry-form', form).forEach((entryForm) => {
    jsonData.entries.push(entryFormToJSON(entryForm));
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

export default function initExtract() {
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
