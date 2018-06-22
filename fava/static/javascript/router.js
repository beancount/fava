// Routing
//
// Fava intercepts all clicks on links and will in most cases asynchronously
// load the content of the page and replace the <article> contents with them.

import { $, $$ } from './helpers';
import e from './events';
import initSort from './sort';
import handleHash from './overlays';

// Set the query string to match the filter inputs and the interval and
// conversion <select>'s.
function updateURL(url) {
  const newURL = new URL(url);
  const currentURL = new URL(window.location.href);
  ['account', 'filter', 'time'].forEach((filter) => {
    newURL.searchParams.delete(filter);
    const el = $(`#${filter}-filter`);
    if (el.value) {
      newURL.searchParams.set(filter, el.value);
    }
  });

  ['interval', 'charts', 'conversion'].forEach((setting) => {
    if (currentURL.searchParams.has(setting)) {
      newURL.searchParams.set(setting, currentURL.searchParams.get(setting));
    } else {
      newURL.searchParams.delete(setting);
    }
  });

  return newURL.toString();
}

class Router {
  // This should be called once when the page has been loaded. Initializes the
  // router and takes over clicking on links.
  init() {
    handleHash();
    this.updateState();

    window.addEventListener('popstate', () => {
      if (window.location.hash !== this.state.hash
          && window.location.pathname === this.state.pathname
          && window.location.search === this.state.search) {
        handleHash();
        this.updateState();
      } else if (window.location.pathname !== this.state.pathname
                || window.location.search !== this.state.search) {
        this.loadURL(window.location.href, false);
      }
    });

    this.takeOverLinks();
  }

  // Go to URL. If load is `true`, load the page at URL, otherwise only update
  // the current state.
  navigate(url, load = true) {
    if (load) {
      this.loadURL(url);
    } else {
      window.history.pushState(null, null, url);
      this.updateState();
    }
  }

  // Replace <article> contents with the page at `url`. If `historyState` is
  // false, do not create a history state and do not scroll to top.
  loadURL(url, historyState = true) {
    const state = { interrupt: false };
    e.trigger('navigate', state);
    if (state.interrupt) { return; }

    const getUrl = new URL(url);
    getUrl.searchParams.set('partial', true);

    const svg = $('header svg');
    svg.classList.add('loading');

    $.fetch(getUrl.toString())
      .then((response) => {
        response.text()
          .then((data) => {
            if (!response.ok) {
              e.trigger('error', data);
              return;
            }
            if (historyState) {
              window.history.pushState(null, null, url);
              window.scroll(0, 0);
            }
            this.updateState();
            $('article').innerHTML = data;
            e.trigger('page-loaded');
            handleHash();
          });
      }, () => {
        e.trigger('error', `Loading ${url} failed.`);
      })
      .finally(() => {
        svg.classList.remove('loading');
      });
  }

  // Update the routers state object. The state object is used to distinguish
  // between the user navigating the browser history or the hash changing.
  updateState() {
    this.state = {
      hash: window.location.hash,
      pathname: window.location.pathname,
      search: window.location.search,
    };
  }

  // Intercept all clicks on links (<a>) and .navigate() to the link instead.
  // Doesn't intercept if
  //  - a modifier key is pressed,
  //  - the link starts with a hash '#', or
  //  - the link has a `data-remote` attribute.
  takeOverLinks() {
    $.delegate(window.document, 'click', 'a', (event) => {
      if (event.button !== 0 || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) {
        return;
      }
      const link = event.target.closest('a');
      if (link.getAttribute('href').charAt(0) === '#' || link.host !== window.location.host) {
        return;
      }

      if (!event.defaultPrevented
          && !link.hasAttribute('data-remote')
          && link.protocol.indexOf('http') === 0) {
        event.preventDefault();

        // update sidebar links
        if (link.parentNode.parentNode.parentNode.tagName === 'ASIDE') {
          this.navigate(updateURL(link.href));
        } else {
          this.navigate(link.href);
        }
      }
    });
  }
}

const router = new Router();
export default router;

e.on('reload', () => {
  router.loadURL(window.location.href, false);
});

e.on('button-click-reload-page', () => {
  e.trigger('reload');
});

e.on('form-submit-filters', () => {
  router.navigate(updateURL(window.location.href));
});

e.on('form-submit-query', (form) => {
  const queryString = form.elements.query_string.value.trim();
  if (queryString === '') {
    return;
  }

  const url = new URL(window.location);
  url.searchParams.set('query_string', queryString);

  const pageURL = url.toString();
  url.searchParams.set('result_only', true);

  $.fetch(url.toString())
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

// These elements might be added asynchronously, so rebind them on page-load.
e.on('page-loaded', () => {
  const interval = $('#chart-interval');
  if (interval) {
    interval.addEventListener('change', () => {
      const newURL = new URL(window.location.href);
      newURL.searchParams.set('interval', interval.value);
      if (interval.value === interval.getAttribute('data-default')) {
        newURL.searchParams.delete('interval');
      }
      router.navigate(newURL.toString());
    });
  }

  const conversion = $('#conversion');
  if (conversion) {
    conversion.addEventListener('change', () => {
      const newURL = new URL(window.location.href);
      newURL.searchParams.set('conversion', conversion.value);
      if (conversion.value === 'at_cost') {
        newURL.searchParams.delete('conversion');
      }
      router.navigate(newURL.toString());
    });
  }
});
