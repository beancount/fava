import Awesomplete from 'awesomplete';
import URI from 'urijs';

import { $, $$ } from './helpers';

function updateInput(input) {
  const isEmpty = !input.value;

  if (input.value.length > input.getAttribute('placeholder').length) {
    input.setAttribute('size', input.value.length + 2);
  } else {
    input.setAttribute('size', input.getAttribute('placeholder').length + 2);
  }

  input.closest('span').classList.toggle('empty', isEmpty);
}

export function updateFilters() {
  ['account', 'from', 'payee', 'tag', 'time'].forEach((filter) => {
    const value = new URI(window.location).search(true)[filter];
    if (value) {
      const el = document.getElementById(`${filter}-filter`);
      el.value = value;
      updateInput(el);
    }
  });
}

export function initFilters() {
  $$('#filter-form input').forEach((input) => {
    input.addEventListener('awesomplete-selectcomplete', () => {
      updateInput(input);
      $('#filter-form').dispatchEvent(new Event('submit'));
    });

    input.addEventListener('input', () => {
      updateInput(input);
    });
  });

  $$('#filter-form input[type="text"]').forEach((el) => {
    let options = {
      minChars: 0,
      maxItems: 30,
      sort: false,
    };

    if (el.getAttribute('name') === 'tag') {
      options = $.extend(options, {
        filter(text, input) {
          return Awesomplete.FILTER_CONTAINS(text, input.match(/[^,]*$/)[0]); // eslint-disable-line new-cap, max-len
        },
        replace(text) {
          const before = this.input.value.match(/^.+,\s*|/)[0];
          this.input.value = `${before}${text}, `;
        },
      });
    }

    const completer = new Awesomplete(el, options);
    const isEmpty = !el.value;

    el.closest('span').classList.toggle('empty', isEmpty);

    el.addEventListener('focus', () => {
      completer.evaluate();
    });
  });

  $$('#filter-form button[type="button"]').forEach((button) => {
    button.addEventListener('click', () => {
      const input = $('input', button.closest('span'));
      input.value = '';
      updateInput(input);

      $('#filter-form').dispatchEvent(new Event('submit'));
    });
  });
}
