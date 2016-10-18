import URI from 'urijs';

import e from './events';

function loadURL(url, noHistoryState) {
  $.get(url, { partial: true })
    .done((data) => {
      if (!noHistoryState) {
        window.history.pushState(null, null, url);
      }
      $('article').html(data);
      e.trigger('page-loaded');
    })
    .fail(() => {
      e.trigger('error', `Loading ${url} failed.`);
    });
}

function updateURL(url) {
  const newURL = new URI(url);
  ['account', 'from', 'payee', 'tag', 'time'].forEach((filter) => {
    newURL.removeSearch(filter);
    const el = document.getElementById(`${filter}-filter`);
    if (el.value) {
      newURL.setSearch(filter, el.value);
    }
  });
  const interval = document.getElementById('chart-interval');
  if (interval) {
    newURL.setSearch('interval', interval.value);
    if (interval.value === interval.dataset.default) {
      newURL.removeSearch('interval');
    }
  }
  return newURL.toString();
}

export default function initRouter() {
  window.addEventListener('popstate', () => {
    loadURL(window.location.pathname, true);
  });

  $(document).on('click', 'a', (event) => {
    const link = event.currentTarget;
    let href = link.getAttribute('href');

    const isHttp = link.protocol.indexOf('http') === 0;
    const format = (href.indexOf('.') > 0) ? href.slice(href.indexOf('.') + 1) : 'html';
    const isRemote = link.dataset.remote;

    if (!event.isDefaultPrevented() && !isRemote && isHttp && format === 'html') {
      event.preventDefault();

      // update sidebar links
      if (link.parentNode.parentNode.parentNode.tagName === 'ASIDE') {
        href = updateURL(href);
      }
      loadURL(href);
    }
  });

  $('#reload-page').click((event) => {
    event.preventDefault();
    loadURL(window.location.pathname);
  });

  $(document).on('submit', '#filter-form', (event) => {
    event.preventDefault();
    loadURL(updateURL(window.location.pathname));
  });

  $(document).on('submit', '#query-form', (event) => {
    event.preventDefault();
    const url = new URI(window.location.pathname)
      .setSearch('query_string', $('#query-editor').val())
      .toString();
    $.get(url, { partial: true, result_only: true }, (data) => {
      $('#query-container').html(data);
    });
  });

  $(document).on('change', '#chart-interval', (event) => {
    event.preventDefault();
    loadURL(updateURL(window.location.pathname));
  });
}
