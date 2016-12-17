import Mousetrap from 'mousetrap';
import 'mousetrap/plugins/bind-dictionary/mousetrap-bind-dictionary';

import { $, $$ } from './helpers';

function click(selector) {
  const element = $(selector);
  if (element) {
    element.click();
  }
}

export function updateKeyboardShortcuts() {
  // Change page
  $$('aside a').forEach((element) => {
    const key = element.getAttribute('data-key');
    if (key !== undefined) {
      Mousetrap.bind(key, () => {
        element.click();
      });
    }
  });
}

export function initKeyboardShortcuts() {
  Mousetrap.bind({
    '?': () => {
      $('#keyboard-shortcuts').classList.add('shown');
    },
    esc() {
      $$('.overlay-wrapper').forEach((el) => {
        el.classList.remove('shown');
      });
    },
    n() {
      $('#add-transaction-button').click();
    },
  }, 'keyup');

  // Filtering:
  Mousetrap.bind({
    'f f': () => {
      $('#from-filter').focus();
    },
    'f t': () => {
      $('#time-filter').focus();
    },
    'f g': () => {
      $('#tag-filter').focus();
    },
    'f a': () => {
      $('#account-filter').focus();
    },
    'f p': () => {
      $('#payee-filter').focus();
    },
  }, 'keyup');

  // Charts
  Mousetrap.bind({
    'ctrl+c': () => {
      click('#toggle-chart');
    },
    c() {
      const selected = $('#chart-labels .selected');

      if (selected && selected.nextElementSibling) {
        selected.nextElementSibling.click();
      } else {
        click('#chart-labels label:first-child');
      }
    },
    'shift+c': () => {
      const selected = $('#chart-labels .selected');

      if (selected && selected.previousElementSibling) {
        selected.previousElementSibling.click();
      } else {
        click('#chart-labels label:last-child');
      }
    },
  }, 'keyup');

  // Journal
  Mousetrap.bind({
    p() {
      click('#entry-filters button[data-type=postings]');
    },
    m() {
      click('#entry-filters button[data-type=metadata]');
    },

    's o': () => {
      click('#entry-filters button[data-type=open]');
    },
    's c': () => {
      click('#entry-filters button[data-type=close]');
    },
    's t': () => {
      click('#entry-filters button[data-type=transaction]');
    },
    's b': () => {
      click('#entry-filters button[data-type=balance]');
    },
    's n': () => {
      click('#entry-filters button[data-type=note]');
    },
    's d': () => {
      click('#entry-filters button[data-type=document]');
    },
    's p': () => {
      click('#entry-filters button[data-type=pad]');
    },
    's q': () => {
      click('#entry-filters button[data-type=query]');
    },
    's shift+c': () => {
      click('#entry-filters button[data-type=custom]');
    },
    's shift+b': () => {
      click('#entry-filters button[data-type=budget]');
    },

    't c': () => {
      click('#entry-filters button[data-type=cleared]');
    },
    't p': () => {
      click('#entry-filters button[data-type=pending]');
    },
    't o': () => {
      click('#entry-filters button[data-type=other]');
    },
    'd d': () => {
      click('#entry-filters button[data-type=discovered]');
    },
    'd s': () => {
      click('#entry-filters button[data-type=statement]');
    },
  }, 'keyup');
}
