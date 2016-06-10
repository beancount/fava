/* global Awesomplete */
require('awesomplete');

module.exports.initFilters = function initFilters() {
  $('#filter-form input').on('input awesomplete-selectcomplete', function() {
    const $this = $(this);
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

  $('#filter-form input[type="text"]').each(function() {
    let options = {
      minChars: 0,
      maxItems: 30,
    };

    if ($(this).attr('name') === 'tag' || $(this).attr('name') === 'payee') {
      options = $.extend(options, {
        filter(text, input) {
          return Awesomplete.FILTER_CONTAINS(text, input.match(/[^,]*$/)[0]);
        },
        replace(text) {
          const before = this.input.value.match(/^.+,\s*|/)[0];
          this.input.value = before + text + ', ';
        },
      });
    }

    const completer = new Awesomplete(this, options);
    const isEmpty = !$(this).val();

    $(this).parents('li')
        .toggleClass('empty', isEmpty)
      .find('button')
        .toggle(!isEmpty);

    $(this).focus(() => {
      completer.evaluate();
    });
  });

  $('#filter-form button').click(function() {
    $(this).parents('li')
      .find('input')
        .val('');
    $('#filter-form').submit();
  });
};
