const Awesomplete = require('awesomplete');
const URI = require('urijs');

function updateInput(input) {
  const isEmpty = !input.value;

  if (input.value.length > input.getAttribute('placeholder').length) {
    input.setAttribute('size', input.value.length + 2);
  } else {
    input.setAttribute('size', input.getAttribute('placeholder').length + 2);
  }

  $(input).parents('span')
      .toggleClass('empty', isEmpty);
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
  $('#filter-form input').on('awesomplete-selectcomplete', (event) => {
    updateInput(event.currentTarget);
    $('#filter-form').submit();
  });

  $('#filter-form input').on('input', (event) => {
    updateInput(event.currentTarget);
  });

  $('#filter-form input[type="text"]').each((_, el) => {
    let options = {
      minChars: 0,
      maxItems: 30,
      sort(text, input) {
        const order = el.getAttribute('name') === 'time' ? -1 : 1;
        return text.value.localeCompare(input.value) * order;
      },
    };

    if (el.getAttribute('name') === 'tag' || el.getAttribute('name') === 'payee') {
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

    $(el).parents('span')
        .toggleClass('empty', isEmpty);

    $(el).focus(() => {
      completer.evaluate();
    });
  });

  $('#filter-form button').click((event) => {
    $(event.currentTarget).parents('span')
      .find('input')
        .val('')
        .each((_, el) => { updateInput(el); });

    $('#filter-form').submit();
  });
}
