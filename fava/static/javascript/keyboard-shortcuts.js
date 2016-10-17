const Mousetrap = require('mousetrap');
require('mousetrap/plugins/bind-dictionary/mousetrap-bind-dictionary');

export function updateKeyboardShortcuts() {
  // Change page
  $('aside a').each((index, element) => {
    const key = element.dataset.key;
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
      document.getElementById('keyboard-shortcuts').classList.add('shown');
    },
    esc() {
      $('.overlay-wrapper').removeClass('shown');
    },
  }, 'keyup');

  // Filtering:
  Mousetrap.bind({
    'f f': () => {
      document.getElementById('from-filter').focus();
    },
    'f t': () => {
      document.getElementById('time-filter').focus();
    },
    'f g': () => {
      document.getElementById('tag-filter').focus();
    },
    'f a': () => {
      document.getElementById('account-filter').focus();
    },
    'f p': () => {
      document.getElementById('payee-filter').focus();
    },
  }, 'keyup');

  // Charts
  Mousetrap.bind({
    'ctrl+c': () => {
      document.getElementById('toggle-chart').click();
    },
    c() {
      const next = $('#chart-labels .selected').next();

      if (next.length) {
        next.click();
      } else {
        $('#chart-labels label:first-child').click();
      }
    },
    'shift+c': () => {
      const prev = $('#chart-labels .selected').prev();

      if (prev.length) {
        prev.click();
      } else {
        $('#chart-labels label:last-child').click();
      }
    },
  }, 'keyup');

  // Journal
  Mousetrap.bind({
    l() {
      $('#entry-filters button[data-type=postings]').click();
    },
    m() {
      $('#entry-filters button[data-type=metadata]').click();
    },

    's o': () => {
      $('#entry-filters button[data-type=open]').click();
    },
    's c': () => {
      $('#entry-filters button[data-type=close]').click();
    },
    's t': () => {
      $('#entry-filters button[data-type=transaction]').click();
    },
    's b': () => {
      $('#entry-filters button[data-type=balance]').click();
    },
    's n': () => {
      $('#entry-filters button[data-type=note]').click();
    },
    's d': () => {
      $('#entry-filters button[data-type=document]').click();
    },
    's p': () => {
      $('#entry-filters button[data-type=pad]').click();
    },
    's q': () => {
      $('#entry-filters button[data-type=query]').click();
    },
    's shift+c': () => {
      $('#entry-filters button[data-type=custom]').click();
    },
    's shift+b': () => {
      $('#entry-filters button[data-type=budget]').click();
    },

    't c': () => {
      $('#entry-filters button[data-type=cleared]').click();
    },
    't p': () => {
      $('#entry-filters button[data-type=pending]').click();
    },
    't o': () => {
      $('#entry-filters button[data-type=other]').click();
    },
  }, 'keyup');
}
