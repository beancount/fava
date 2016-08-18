/* global Awesomplete */
require('awesomplete');

module.exports.initFilters = function initFilters() {
  $('#filter-form input').on('input awesomplete-selectcomplete', event => {
    const $this = $(event.currentTarget);
    const isEmpty = !$this.val();

    if ($this.val().length > $this.attr('placeholder').length) {
      $this.attr('size', $this.val().length + 2);
    } else {
      $this.attr('size', $this.attr('placeholder').length + 2);
    }

    $this.parents('li')
        .toggleClass('empty', isEmpty)
      .find('button')
        .toggle(!isEmpty);
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

    $el.parents('li')
        .toggleClass('empty', isEmpty)
      .find('button')
        .toggle(!isEmpty);

    $el.focus(() => {
      completer.evaluate();
    });
  });

  $('#filter-form button').click(event => {
    $(event.currentTarget).parents('li')
      .find('input')
        .val('');
    $('#filter-form').submit();
  });
};
