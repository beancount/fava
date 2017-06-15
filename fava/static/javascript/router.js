// Routing
//
// Fava intercepts all clicks on links and will in most cases asynchronously
// load the content of the page and replace the <article> contents with them.

import URI from 'urijs';

import { $, $$ } from './helpers';
import e from './events';
import initEditor from './editor';
import initSort from './sort';
import { showTransactionOverlay } from './transaction-overlay';

// Replace <article> contents with the page at `url`. If `noHistoryState` is
// true, do not create a history state.
function loadURL(url, noHistoryState) {
  const getUrl = new URI(url)
    .setSearch('partial', true)
    .toString();

  const svg = $('header svg');
  svg.classList.add('loading');

  $.fetch(getUrl)
    .then(response => response.text())
    .then((data) => {
      svg.classList.remove('loading');
      if (!noHistoryState) {
        window.history.pushState(null, null, url);
      }
      $('article').innerHTML = data;
      e.trigger('page-loaded');
    }, () => {
      svg.classList.remove('loading');
      e.trigger('error', `Loading ${url} failed.`);
    });
}

// Set the query string to match the filter inputs and the interval and
// conversion <select>'s.
function updateURL(url) {
  const newURL = new URI(url);
  ['account', 'from', 'payee', 'tag', 'time'].forEach((filter) => {
    newURL.removeSearch(filter);
    const el = $(`#${filter}-filter`);
    if (el.value) {
      newURL.setSearch(filter, el.value);
    }
  });
  const interval = $('#chart-interval');
  if (interval) {
    newURL.setSearch('interval', interval.value);
    if (interval.value === interval.getAttribute('data-default')) {
      newURL.removeSearch('interval');
    }
  }
  const conversion = $('#conversion');
  if (conversion) {
    newURL.setSearch('conversion', conversion.value);
    if (conversion.value === 'at_cost') {
      newURL.removeSearch('conversion');
    }
  }
  return newURL.toString();
}

// Show various overlays depending on the hash.
function handleHash() {
  const hash = window.location.hash;
  if (hash === '#add-transaction') {
    showTransactionOverlay();
  }
  if (hash.startsWith('#context')) {
    $.fetch(`${window.favaAPI.baseURL}_context/?entry_hash=${hash.slice(9)}`)
      .then(response => response.text())
      .then((data) => {
        $('#context-overlay .content').innerHTML = data;
        initEditor();
      }, () => {
        e.trigger('error', 'Loading context failed.');
      });
    $('#context-overlay').classList.add('shown');
  }
}

e.on('reload', () => {
  loadURL(window.location.href);
});

// These elements might be added asynchronously, so rebind them on page-load.
e.on('page-loaded', () => {
  if ($('#query-form')) {
    $('#query-form').addEventListener('submit', (event) => {
      event.preventDefault();
      const queryString = $('#query-editor').value.trim();
      if (queryString === '') {
        return;
      }

      const url = new URI(window.location.href)
        .setSearch('query_string', queryString);

      const pageURL = url.toString();

      const fetchURL = url
        .setSearch('result_only', true)
        .toString();

      $.fetch(fetchURL)
        .then(response => response.text())
        .then((data) => {
          $$('.queryresults-wrapper').forEach((element) => {
            element.classList.add('toggled');
          });
          $('#query-container').insertAdjacentHTML('afterbegin', data);
          initSort();
          window.history.replaceState(null, null, pageURL);
        });
    });
  }

  if ($('#chart-interval')) {
    $('#chart-interval').addEventListener('change', () => {
      loadURL(updateURL(window.location.href));
    });
  }

  if ($('#conversion')) {
    $('#conversion').addEventListener('change', () => {
      loadURL(updateURL(window.location.href));
    });
  }
});

export default function initRouter() {
  if (window.location.hash) {
    handleHash();
  }

  let currentHref = window.location.href;
  let currentHash = window.location.hash;

  window.addEventListener('popstate', () => {
    if (window.location.href === currentHref) {
      return;
    }
    currentHref = window.location.href;
    if (window.location.hash !== currentHash) {
      currentHash = window.location.hash;
      handleHash();
    } else {
      loadURL(window.location.href, true);
    }
  });

  $.delegate(document, 'click', 'a', (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) {
      return;
    }
    const link = event.target.closest('a');
    let href = link.getAttribute('href');
    if (href.charAt(0) === '#') {
      return;
    }

    const isHttp = link.protocol.indexOf('http') === 0;
    const suffix = URI(href).suffix();
    const isRemote = link.getAttribute('data-remote');

    if (!event.defaultPrevented && !isRemote && isHttp && (!suffix || suffix === 'html')) {
      event.preventDefault();

      // update sidebar links
      if (link.parentNode.parentNode.parentNode.tagName === 'ASIDE') {
        href = updateURL(href);
      }
      loadURL(href);
    }
  });

  $('#reload-page').addEventListener('click', () => {
    e.trigger('reload');
  });

  $('#filter-form').addEventListener('submit', (event) => {
    event.preventDefault();
    loadURL(updateURL(window.location.href));
  });
}
