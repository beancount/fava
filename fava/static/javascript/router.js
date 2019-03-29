// Routing
//
// Fava intercepts all clicks on links and will in most cases asynchronously
// load the content of the page and replace the <article> contents with them.

import { select, selectAll, delegate, fetch, handleText } from "./helpers";
import e from "./events";
import { notify } from "./notifications";
import initSort from "./sort";
import { urlHash, conversion, interval, showCharts } from "./stores";

// Set the query string to match the filter inputs and the interval and
// conversion <select>'s.
function updateURL(url) {
  const newURL = new URL(url);
  const currentURL = new URL(window.location.href);
  ["account", "filter", "time"].forEach(filter => {
    newURL.searchParams.delete(filter);
    const el = select(`#${filter}-filter`);
    if (el.value) {
      newURL.searchParams.set(filter, el.value);
    }
  });

  ["interval", "charts", "conversion"].forEach(setting => {
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
    urlHash.set(window.location.hash.slice(1));
    this.updateState();

    window.addEventListener("popstate", () => {
      if (
        window.location.hash !== this.state.hash &&
        window.location.pathname === this.state.pathname &&
        window.location.search === this.state.search
      ) {
        urlHash.set(window.location.hash.slice(1));
        this.updateState();
      } else if (
        window.location.pathname !== this.state.pathname ||
        window.location.search !== this.state.search
      ) {
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
  async loadURL(url, historyState = true) {
    const state = { interrupt: false };
    e.trigger("navigate", state);
    if (state.interrupt) {
      return;
    }

    const getUrl = new URL(url);
    getUrl.searchParams.set("partial", true);

    const svg = select(".fava-icon");
    svg.classList.add("loading");

    try {
      const content = await fetch(getUrl.toString()).then(handleText);
      if (historyState) {
        window.history.pushState(null, null, url);
        window.scroll(0, 0);
      }
      this.updateState();
      select("article").innerHTML = content;
      e.trigger("page-loaded");
      urlHash.set(window.location.hash.slice(1));
    } catch (error) {
      notify(`Loading ${url} failed.`, "error");
    } finally {
      svg.classList.remove("loading");
    }
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
    delegate(window.document, "click", "a", event => {
      if (
        event.button !== 0 ||
        event.altKey ||
        event.ctrlKey ||
        event.metaKey ||
        event.shiftKey
      ) {
        return;
      }
      const link = event.target.closest("a");
      if (
        link.getAttribute("href").charAt(0) === "#" ||
        link.host !== window.location.host
      ) {
        return;
      }

      if (
        !event.defaultPrevented &&
        !link.hasAttribute("data-remote") &&
        link.protocol.indexOf("http") === 0
      ) {
        event.preventDefault();

        // update sidebar links
        if (link.closest("aside")) {
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

e.on("reload", () => {
  router.loadURL(window.location.href, false);
});

e.on("button-click-reload-page", () => {
  e.trigger("reload");
});

e.on("form-submit-filters", () => {
  router.navigate(updateURL(window.location.href));
});

e.on("form-submit-query", form => {
  const queryString = form.elements.query_string.value.trim();
  if (queryString === "") {
    return;
  }

  const url = new URL(window.location);
  url.searchParams.set("query_string", queryString);

  const pageURL = url.toString();
  url.searchParams.set("result_only", true);

  fetch(url.toString())
    .then(handleText)
    .then(data => {
      selectAll(".queryresults-wrapper").forEach(element => {
        element.classList.add("toggled");
      });
      select("#query-container").insertAdjacentHTML("afterbegin", data);
      initSort();
      window.history.replaceState(null, null, pageURL);
    });
});

e.on("page-init", () => {
  const params = new URL(window.location.href).searchParams;
  showCharts.set(!(params.get("charts") === "false"));
  interval.set(params.get("interval") || window.favaAPI.favaOptions.interval);
  conversion.set(params.get("conversion") || "at_cost");

  interval.subscribe(value => {
    const newURL = new URL(window.location.href);
    newURL.searchParams.set("interval", value);
    if (value === window.favaAPI.favaOptions.interval) {
      newURL.searchParams.delete("interval");
    }
    const url = newURL.toString();
    if (url !== window.location.href) {
      router.navigate(url);
    }
  });

  conversion.subscribe(value => {
    const newURL = new URL(window.location.href);
    newURL.searchParams.set("conversion", value);
    if (value === "at_cost") {
      newURL.searchParams.delete("conversion");
    }
    const url = newURL.toString();
    if (url !== window.location.href) {
      router.navigate(url);
    }
  });

  showCharts.subscribe(value => {
    const newURL = new URL(window.location.href);
    if (value) {
      newURL.searchParams.delete("charts");
    } else {
      newURL.searchParams.set("charts", false);
    }
    router.navigate(newURL.toString(), false);
  });
});
