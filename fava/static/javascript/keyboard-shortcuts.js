const Mousetrap = require('mousetrap');
require('mousetrap/plugins/bind-dictionary/mousetrap-bind-dictionary');

module.exports.init = function init() {
  Mousetrap.bind({
    '?': () => {
      $('#keyboard-shortcuts.overlay-wrapper').show();
    },
    esc() {
      $('.overlay-wrapper').hide();
    },
  }, 'keyup');

  // Filtering:
  Mousetrap.bind({
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
      $('#name-filter').focus();
    },
  }, 'keyup');

  Mousetrap.bind(window.keyBindings, 'keyup');

  // Charts
  Mousetrap.bind({
    'ctrl+c': () => {
      $('#toggle-chart').click();
    },
    c() {
      const next = $('#chart-labels label.selected').next();
      $('#chart-labels label').removeClass('selected');
      if (next.length) {
        next.click();
      } else {
        $('#chart-labels label:first-child').click();
      }
    },
    'shift+c': () => {
      const prev = $('#chart-labels label.selected').prev();
      $('#chart-labels label').removeClass('selected');

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
      $('#entry-filters button[data-type=legs]').click();
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
};
