import URI from 'urijs';

import { $ } from './helpers';
import e from './events';

const jQuery = require('jquery');

function loadURL(url, noHistoryState) {
  jQuery.get(url, { partial: true })
    .done((data) => {
      if (!noHistoryState) {
        window.history.pushState(null, null, url);
      }
      jQuery('article').html(data);
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
    if (interval.value === interval.getAttribute('data-default')) {
      newURL.removeSearch('interval');
    }
  }
  return newURL.toString();
}

e.on('reload', () => {
  loadURL(window.location.pathname);
});

export default function initRouter() {
  window.addEventListener('popstate', () => {
    loadURL(window.location.pathname, true);
  });

  $.delegate(document, 'click', 'a', (event) => {
    const link = event.target.closest('a');
    let href = link.getAttribute('href');

    const isHttp = link.protocol.indexOf('http') === 0;
    const format = (href.indexOf('.') > 0) ? href.slice(href.indexOf('.') + 1) : 'html';
    const isRemote = link.getAttribute('data-remote');

    if (!event.defaultPrevented && !isRemote && isHttp && format === 'html') {
      event.preventDefault();

      // update sidebar links
      if (link.parentNode.parentNode.parentNode.tagName === 'ASIDE') {
        href = updateURL(href);
      }
      loadURL(href);
    }
  });

  $('#reload-page').addEventListener('click', (event) => {
    event.preventDefault();
    e.trigger('reload');
  });

  $('#filter-form').addEventListener('submit', (event) => {
    event.preventDefault();
    loadURL(updateURL(window.location.pathname));
  });

  // These elements might be added asynchronously, so rebind them on page-load.
  e.on('page-loaded', () => {
    if ($('#query-form')) {
      $('#query-form').addEventListener('submit', (event) => {
        event.preventDefault();
        const url = new URI(window.location.pathname)
          .setSearch('query_string', $('#query-editor').value)
          .setSearch('partial', true)
          .setSearch('result_only', true)
          .toString();

        fetch(url)
          .then((response) => {
            response.text()
              .then((data) => {
                $('#query-container').innerHTML = data;
              });
          });
      });
    }

    if ($('#chart-interval')) {
      $('#chart-interval').addEventListener('change', () => {
        loadURL(updateURL(window.location.pathname));
      });
    }
  });
}
