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
  /** The URL hash. */
  hash: string;

  /** The URL pathname. */
  pathname: string;

  /** The URL search string. */
  search: string;

  interruptHandlers: Set<() => string | null>;

  constructor() {
    this.hash = window.location.hash;
    this.pathname = window.location.pathname;
    this.search = window.location.search;

    this.interruptHandlers = new Set();
  }

  shouldInterrupt(): string | null {
    for (const handler of this.interruptHandlers) {
      const ret = handler();
      if (ret) {
        return ret;
      }
    }
    return null;
  }

  // This should be called once when the page has been loaded. Initializes the
  // router and takes over clicking on links.
  init(): void {
    urlHash.set(window.location.hash.slice(1));
    this.updateState();

    window.addEventListener("beforeunload", event => {
      const leaveMessage = this.shouldInterrupt();
      if (leaveMessage) {
        event.returnValue = leaveMessage;
      }
    });

    window.addEventListener("popstate", () => {
      urlHash.set(window.location.hash.slice(1));
      if (
        window.location.hash !== this.hash &&
        window.location.pathname === this.pathname &&
        window.location.search === this.search
      ) {
        this.updateState();
      } else if (
        window.location.pathname !== this.pathname ||
        window.location.search !== this.search
      ) {
        this.loadURL(window.location.href, false);
      }
    });

    this.takeOverLinks();
  }

  // Go to URL. If load is `true`, load the page at URL, otherwise only update
  // the current state.
  navigate(url: string, load = true): void {
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
  async loadURL(url: string, historyState = true): Promise<void> {
    const leaveMessage = this.shouldInterrupt();
    if (leaveMessage) {
      // eslint-disable-next-line no-alert
      if (!window.confirm(leaveMessage)) {
        return;
      }
    }

    const getUrl = new URL(url);
    getUrl.searchParams.set("partial", "true");

    const svg = select(".fava-icon");
    svg?.classList.add("loading");

    try {
      const content = await fetch(getUrl.toString()).then(handleText);
      if (historyState) {
        window.history.pushState(null, "", url);
        window.scroll(0, 0);
      }
      this.updateState();
      const article = select("article");
      if (article) {
        e.trigger("before-page-loaded");
        article.innerHTML = content;
      }
      e.trigger("page-loaded");
      urlHash.set(window.location.hash.slice(1));
    } catch (error) {
      notify(`Loading ${url} failed: ${error.message}`, "error");
    } finally {
      svg?.classList.remove("loading");
    }
  }

  /*
   * Update the routers state.
   *
   * The routers state is used to distinguish between the user navigating the
   * browser history or the hash changing.
   */
  updateState(): void {
    this.hash = window.location.hash;
    this.pathname = window.location.pathname;
    this.search = window.location.search;
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
  takeOverLinks(): void {
    delegate(
      document,
      "click",
      "a",
      (event: MouseEvent, link: HTMLAnchorElement) => {
        if (
          link.getAttribute("href")?.charAt(0) === "#" ||
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
  reload(): void {
    this.loadURL(window.location.href, false);
  }
}

const router = new Router();
export default router;

e.on("page-init", () => {
  select("#reload-page")?.addEventListener("click", () => {
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
  syncStoreValueToUrl(
    conversion,
    "conversion",
    favaAPI.favaOptions.conversion,
    true
  );
  syncStoreValueToUrl(showCharts, "charts", true, false);
});
