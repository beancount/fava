/* global Awesomplete */
require('awesomplete');
const URI = require('urijs');

function updateInput(input) {
  const isEmpty = !input.val();

  if (input.val().length > input.attr('placeholder').length) {
    input.attr('size', input.val().length + 2);
  } else {
    input.attr('size', input.attr('placeholder').length + 2);
  }

  input.parents('span')
      .toggleClass('empty', isEmpty)
    .find('button')
      .toggle(!isEmpty);
}

module.exports.update = function update() {
  $.each(['account', 'from', 'payee', 'tag', 'time'], (_, filter) => {
    const value = new URI(window.location).search(true)[filter];
    if (value) {
      $(`#${filter}-filter`).val(value);
      updateInput($(`#${filter}-filter`));
    }
  });
};

module.exports.init = function init() {
  $('#filter-form input').on('awesomplete-selectcomplete', (event) => {
    updateInput($(event.currentTarget));
    $('#filter-form').submit();
  });

  $('#filter-form input').on('input', (event) => {
    updateInput($(event.currentTarget));
  });

  $('#filter-form input[type="text"]').each((_, el) => {
    let options = {
      minChars: 0,
      maxItems: 30,
    };
    const $el = $(el);

    if ($el.attr('name') === 'tag' || $el.attr('name') === 'payee') {
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
    const isEmpty = !$el.val();

    $el.parents('span')
        .toggleClass('empty', isEmpty)
      .find('button')
        .toggle(!isEmpty);

    $el.focus(() => {
      completer.evaluate();
    });
  });

  $('#filter-form button').click((event) => {
    $(event.currentTarget).parents('span')
      .find('input')
        .val('')
        .each((_, el) => { updateInput($(el)); });

    $('#filter-form').submit();
  });
};
