const Mousetrap = require('mousetrap');
require('mousetrap/plugins/bind-dictionary/mousetrap-bind-dictionary');

module.exports.global = function global() {
  Mousetrap.bind({
    '?'() {
      $('#keyboard-shortcuts.overlay-wrapper').show();
    },
    esc() {
      $('.overlay-wrapper').hide();
    },
  }, 'keyup');

  // Filtering:
  Mousetrap.bind({
    'f t'() {
      $('#time-filter').focus();
    },
    'f g'() {
      $('#tag-filter').focus();
    },
    'f a'() {
      $('#account-filter').focus();
    },
    'f p'() {
      $('#name-filter').focus();
    },
  }, 'keyup');
};

module.exports.charts = function charts() {
  Mousetrap.bind({
    'ctrl+c'() {
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
    'shift+c'() {
      const prev = $('#chart-labels label.selected').prev();
      $('#chart-labels label').removeClass('selected');

      if (prev.length) {
        prev.click();
      } else {
        $('#chart-labels label:last-child').click();
      }
    },
  }, 'keyup');
};

module.exports.journal = function journal() {
  Mousetrap.bind({
    'l'() {
      $('#toggle-legs').click();
    },
    'm'() {
      $('#toggle-metadata').click();
    },

    's o'() {
      $('#filter-open').click();
    },
    's c'() {
      $('#filter-close').click();
    },
    's t'() {
      $('#filter-transaction').click();
    },
    's b'() {
      $('#filter-balance').click();
    },
    's n'() {
      $('#filter-note').click();
    },
    's d'() {
      $('#filter-document').click();
    },
    's p'() {
      $('#filter-pad').click();
    },
    's q'() {
      $('#filter-query').click();
    },
    's shift+c'() {
      $('#filter-custom').click();
    },
    's shift+b'() {
      $('#filter-budget').click();
    },

    't c'() {
      $('#filter-cleared').click();
    },
    't p'() {
      $('#filter-pending').click();
    },
    't o'() {
      $('#filter-other').click();
    },
  }, 'keyup');
};
