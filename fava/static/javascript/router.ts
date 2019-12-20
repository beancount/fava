// Routing
//
// Fava intercepts all clicks on links and will in most cases asynchronously
// load the content of the page and replace the <article> contents with them.

import { Writable } from "svelte/store";
import { select, delegate, fetch, handleText } from "./helpers";
import e from "./events";
import { notify } from "./notifications";
import {
  urlHash,
  conversion,
  interval,
  filters,
  favaAPI,
  urlSyncedParams,
} from "./stores";
import { showCharts } from "./stores/chart";

class Router {
  state: {
    hash: string;
    pathname: string;
    search: string;
  };

  constructor() {
    this.state = {
      hash: window.location.hash,
      pathname: window.location.pathname,
      search: window.location.search,
    };
  }

  // This should be called once when the page has been loaded. Initializes the
  // router and takes over clicking on links.
  init() {
    urlHash.set(window.location.hash.slice(1));
    this.updateState();

    window.addEventListener("popstate", () => {
      urlHash.set(window.location.hash.slice(1));
      if (
        window.location.hash !== this.state.hash &&
        window.location.pathname === this.state.pathname &&
        window.location.search === this.state.search
      ) {
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
  navigate(url: string, load = true) {
    if (load) {
      this.loadURL(url);
    } else {
      window.history.pushState(null, "", url);
      this.updateState();
    }
  }

  /*
   * Replace <article> contents with the page at `url`.
   *
   * If `historyState` is false, do not create a history state and do not
   * scroll to top.
   */
  async loadURL(url: string, historyState = true) {
    const state = { interrupt: false };
    e.trigger("navigate", state);
    if (state.interrupt) {
      return;
    }

    const getUrl = new URL(url);
    getUrl.searchParams.set("partial", "true");

    const svg = select(".fava-icon");
    if (svg) {
      svg.classList.add("loading");
    }

    try {
      const content = await fetch(getUrl.toString()).then(handleText);
      if (historyState) {
        window.history.pushState(null, "", url);
        window.scroll(0, 0);
      }
      this.updateState();
      const article = select("article");
      if (article) {
        article.innerHTML = content;
      }
      e.trigger("page-loaded");
      urlHash.set(window.location.hash.slice(1));
    } catch (error) {
      notify(`Loading ${url} failed.`, "error");
    } finally {
      if (svg) {
        svg.classList.remove("loading");
      }
    }
  }

  /*
   * Update the routers state object.
   *
   * The state object is used to distinguish between the user navigating the
   * browser history or the hash changing.
   */
  updateState() {
    this.state = {
      hash: window.location.hash,
      pathname: window.location.pathname,
      search: window.location.search,
    };
  }

  /*
   * Intercept all clicks on links (<a>) and .navigate() to the link instead.
   *
   * Doesn't intercept if
   *  - a button different from the main button is used,
   *  - a modifier key is pressed,
   *  - the link starts with a hash '#', or
   *  - the link has a `data-remote` attribute.
   */
  takeOverLinks() {
    delegate(
      document,
      "click",
      "a",
      (event: MouseEvent, link: HTMLAnchorElement) => {
        if (
          (link.getAttribute("href") || "").charAt(0) === "#" ||
          link.host !== window.location.host ||
          link.hasAttribute("data-remote") ||
          link.protocol.indexOf("http") !== 0 ||
          event.defaultPrevented
        ) {
          return;
        }
        // update sidebar links
        if (link.closest("aside")) {
          const newURL = new URL(link.href);
          const oldParams = new URL(window.location.href).searchParams;
          for (const name of urlSyncedParams) {
            const value = oldParams.get(name);
            if (value) {
              newURL.searchParams.set(name, value);
            } else {
              newURL.searchParams.delete(name);
            }
          }
          link.href = newURL.toString();
        }
        if (
          event.button !== 0 ||
          event.altKey ||
          event.ctrlKey ||
          event.metaKey ||
          event.shiftKey
        ) {
          return;
        }

        event.preventDefault();
        this.navigate(link.href);
      }
    );
  }

  /*
   * Reload the page.
   */
  reload() {
    this.loadURL(window.location.href, false);
  }
}

const router = new Router();
export default router;

e.on("page-init", () => {
  select("#reload-page")!.addEventListener("click", () => {
    router.reload();
  });

  const params = new URL(window.location.href).searchParams;

  filters.set({
    time: params.get("time") || "",
    filter: params.get("filter") || "",
    account: params.get("account") || "",
  });
  filters.subscribe(fs => {
    const newURL = new URL(window.location.href);
    for (const name of Object.keys(fs)) {
      const value = fs[name as keyof typeof fs];
      if (value) {
        newURL.searchParams.set(name, value);
      } else {
        newURL.searchParams.delete(name);
      }
    }
    const url = newURL.toString();
    if (url !== window.location.href) {
      router.navigate(url);
    }
  });

  function syncStoreValueToUrl<T extends boolean | string>(
    store: Writable<T>,
    name: string,
    defaultValue: T,
    shouldLoad: boolean
  ): void {
    let value: T;
    if (typeof defaultValue === "boolean") {
      value = (params.get(name) !== "false" && defaultValue) as T;
    } else {
      value = (params.get(name) as T) || defaultValue;
    }
    store.set(value);

    store.subscribe((val: T) => {
      const newURL = new URL(window.location.href);
      newURL.searchParams.set(name, val.toString());
      if (val === defaultValue) {
        newURL.searchParams.delete(name);
      }
      const url = newURL.toString();
      if (url !== window.location.href) {
        router.navigate(url, shouldLoad);
      }
    });
  }

  // Set initial values from URL and update URL on store changes
  syncStoreValueToUrl(interval, "interval", favaAPI.favaOptions.interval, true);
  syncStoreValueToUrl(conversion, "conversion", "at_cost", true);
  syncStoreValueToUrl(showCharts, "charts", true, false);
});
