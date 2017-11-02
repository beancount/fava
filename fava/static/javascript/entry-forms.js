import { $, $$ } from './helpers';
import e from './events';


export function addPostingRow(form) {
  const newPosting = $('#posting-template').cloneNode(true);
  form.querySelector('.postings').appendChild(newPosting);
  newPosting.setAttribute('id', '');
  return newPosting;
}

export function addMetadataRow(form) {
  const newMetadata = $('#metadata-template').cloneNode(true);
  form.querySelector('.metadata').appendChild(newMetadata);
  newMetadata.setAttribute('id', '');
  return newMetadata;
}

export function entryFormToJSON(form) {
  const entryData = {};
  entryData.type = form.getAttribute('data-type');

  $$('input', form.querySelector('.fieldset')).forEach((input) => {
    entryData[input.name] = input.value;
  });

  entryData.metadata = {};
  $$('.metadata-row', form).forEach((metadata) => {
    const key = metadata.querySelector('input[name=metadata-key]').value;
    if (key) {
      entryData.metadata[key] = metadata.querySelector('input[name=metadata-value]').value;
    }
  });

  if (entryData.type === 'transaction') {
    entryData.postings = [];
    $$('.posting', form).forEach((posting) => {
      const account = posting.querySelector('input[name=account]').value;

      if (account) {
        entryData.postings.push({
          account,
          number: posting.querySelector('input[name=number]').value,
          currency: posting.querySelector('input[name=currency]').value,
        });
      }
    });
  }

  return entryData;
}

function initEntryForm(div) {
  if (div.classList.contains('transaction')) {
    $.delegate(div, 'click', '.add-posting', () => {
      const newPosting = addPostingRow(div);
      newPosting.querySelector('.account').focus();
    });

    $.delegate(div, 'click', '.add-metadata', () => {
      const newMetadata = addMetadataRow(div);
      newMetadata.querySelector('.metadata-key').focus();
    });
  }
}

e.on('page-init', () => {
  $$('#transaction-form .entry-form').forEach(initEntryForm);
});

e.on('page-loaded', () => {
  $$('article .entry-form').forEach(initEntryForm);
});
