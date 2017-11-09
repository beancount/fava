import { $, $$ } from './helpers';
import e from './events';

// Adjust the size of the input element.
function updateInput(input) {
  const size = Math.max(input.value.length, input.getAttribute('placeholder').length);
  input.setAttribute('size', size + 1);

  const isEmpty = !input.value;
  input.closest('span').classList.toggle('empty', isEmpty);
}

e.on('page-loaded', () => {
  ['account', 'from', 'payee', 'tag', 'time'].forEach((filter) => {
    const value = new URLSearchParams(window.location.search).get(filter);
    const el = document.getElementById(`${filter}-filter`);
    if (value) {
      el.value = value;
    }
    updateInput(el);
  });
});

e.on('page-init', () => {
  $$('#filter-form input').forEach((input) => {
    input.addEventListener('autocomplete-select', () => {
      updateInput(input);
      $('#filter-form [type=submit]').click();
    });

    input.addEventListener('input', () => {
      updateInput(input);
    });
  });

  $$('#filter-form button[type="button"]').forEach((button) => {
    button.addEventListener('click', () => {
      const input = $('input', button.closest('span'));
      input.value = '';
      updateInput(input);
      if (new URLSearchParams(window.location.search).get(input.name)) {
        $('#filter-form [type=submit]').click();
      }
    });
  });
});
