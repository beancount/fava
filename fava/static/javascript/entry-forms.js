import { $, $$ } from './helpers';
import e from './events';

// Append a posting row to an .entry-form
export function addPostingRow(form) {
  const newPosting = $('#posting-template').children[0].cloneNode(true);
  form.querySelector('.postings').appendChild(newPosting);
  return newPosting;
}

// Append a metadata row to an .entry-form
function addMetadataRow(form) {
  const newMetadata = $('#metadata-template').children[0].cloneNode(true);
  form.querySelector('.metadata').appendChild(newMetadata);
  return newMetadata;
}

export function entryFormToJSON(form) {
  const entryData = {};
  entryData.type = form.getAttribute('data-type');

  $$('[name]', form).forEach((input) => {
    entryData[input.name] = input.value;
  });

  entryData.metadata = {};
  $$('.metadata-row', form).forEach((metadata) => {
    const key = metadata.querySelector('.metadata-key').value;
    if (key) {
      entryData.metadata[key] = metadata.querySelector('.metadata-value').value;
    }
  });

  if (entryData.type === 'transaction') {
    entryData.postings = [];
    $$('.posting', form).forEach((posting) => {
      const account = posting.querySelector('.account').value;

      if (account) {
        entryData.postings.push({
          account,
          number: posting.querySelector('.number').value,
          currency: posting.querySelector('.currency').value,
        });
      }
    });
  }

  return entryData;
}

function initEntryForm(div) {
  $.delegate(div, 'click', '.add-posting', () => {
    const newPosting = addPostingRow(div);
    newPosting.querySelector('input').focus();
  });

  $.delegate(div, 'click', '.add-metadata', () => {
    const newMetadata = addMetadataRow(div);
    newMetadata.querySelector('input').focus();
  });

  $.delegate(div, 'click', '.remove-fieldset', (event) => {
    event.target.closest('.fieldset').remove();
  });
}

e.on('page-init', () => {
  $$('#transaction-form .entry-form').forEach(initEntryForm);
});

e.on('page-loaded', () => {
  $$('article .entry-form').forEach(initEntryForm);
});
