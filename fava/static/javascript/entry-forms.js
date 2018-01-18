import { $, $$ } from './helpers';
import e from './events';

// Append a posting row to an .entry-form.
function addPostingRow(form) {
  const newPosting = $('#posting-template').children[0].cloneNode(true);
  form.querySelector('.postings').appendChild(newPosting);
  return newPosting;
}

// Append a metadata row to an .entry-form.
function addMetadataRow(form) {
  const newMetadata = $('#metadata-template').children[0].cloneNode(true);
  form.querySelector('.metadata').appendChild(newMetadata);
  return newMetadata;
}

// Reset an entry form.
export function resetEntryForm(form) {
  $$('.metadata', form).forEach((el) => {
    el.remove();
  });
  $$('.posting', form).forEach((el) => {
    el.remove();
  });
  addPostingRow(form);
  addPostingRow(form);
  form.focus();
}

export function entryFormToJSON(form) {
  const entryData = {
    type: form.getAttribute('data-type'),
    metadata: {},
  };

  $$('[name]', form).forEach((input) => {
    entryData[input.name] = input.value;
  });

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

e.on('button-click-remove-fieldset', (button) => {
  button.closest('.fieldset').remove();
});

e.on('button-click-add-metadata', (button) => {
  addMetadataRow(button.closest('.entry-form'))
    .querySelector('input')
    .focus();
});

e.on('button-click-add-posting', (button) => {
  addPostingRow(button.closest('.entry-form'))
    .querySelector('input')
    .focus();
});
