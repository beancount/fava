/**
 * Routing
 *
 * Fava intercepts all clicks on links and will in most cases asynchronously
 * load the content of the page and replace the <article> contents with them.
 */

import type { Writable } from "svelte/store";

import { delegate, Events } from "./lib/events";
import { fetch, handleText } from "./lib/fetch";
import { DEFAULT_INTERVAL, getInterval } from "./lib/interval";
import { log_error } from "./log";
import { notify } from "./notifications";
import { conversion, interval, urlHash } from "./stores";
import { showCharts } from "./stores/chart";
import { account_filter, fql_filter, time_filter } from "./stores/filters";
import { urlSyncedParams } from "./stores/url";

/**
 * Set a store's inital value from the URL.
 */
export function setStoreValuesFromURL(): void {
  const params = new URL(window.location.href).searchParams;
  account_filter.set(params.get("account") ?? "");
  fql_filter.set(params.get("filter") ?? "");
  time_filter.set(params.get("time") ?? "");
  interval.set(getInterval(params.get("interval")));
  conversion.set(params.get("conversion") ?? "at_cost");
  showCharts.set(params.get("charts") !== "false");
}

class Router extends Events<"page-loaded"> {
  /** The URL hash. */
  hash: string;

  /** The URL pathname. */
  pathname: string;

  /** The URL search string. */
  search: string;

  /**
   * Function to intercept navigation, e.g., when there are unsaved changes.
   *
   * If they return a string, that is displayed to the user in an alert to
   * confirm navigation.
   */
  interruptHandlers: Set<() => string | null>;

  constructor() {
    super();

    this.hash = window.location.hash;
    this.pathname = window.location.pathname;
    this.search = window.location.search;

    this.interruptHandlers = new Set();
  }

  /**
   * Check whether any of the registered interruptHandlers wants to stop
   * navigation.
   */
  shouldInterrupt(): string | null {
    for (const handler of this.interruptHandlers) {
      const ret = handler();
      if (ret) {
        return ret;
      }
    }
    return null;
  }

  /**
   * This should be called once when the page has been loaded. Initializes the
   * router and takes over clicking on links.
   */
  init(): void {
    urlHash.set(window.location.hash.slice(1));
    this.updateState();

    window.addEventListener("beforeunload", (event) => {
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
        this.loadURL(window.location.href, false).catch(log_error);
        setStoreValuesFromURL();
      }
    });

    this.takeOverLinks();
  }

  /**
   * Go to URL. If load is `true`, load the page at URL, otherwise only update
   * the current state.
   */
  navigate(url: string, load = true): void {
    if (load) {
      this.loadURL(url).catch(log_error);
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

    const getUrl = new URL(url, window.location.href);
    getUrl.searchParams.set("partial", "true");

    const svg = document.querySelector(".fava-icon");
    svg?.classList.add("loading");

    try {
      const content = await fetch(getUrl.toString()).then(handleText);
      if (historyState) {
        window.history.pushState(null, "", url);
        window.scroll(0, 0);
      }
      this.updateState();
      const article = document.querySelector("article");
      if (article) {
        article.innerHTML = content;
      }
      this.trigger("page-loaded");
      const hash = window.location.hash.slice(1);
      urlHash.set(hash);
      if (hash) {
        document.getElementById(hash)?.scrollIntoView();
      }
    } catch (error) {
      if (error instanceof Error) {
        notify(`Loading ${url} failed: ${error.message}`, "error");
      } else {
        log_error(error);
      }
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
          link.hasAttribute("data-remote") ||
          link.host !== window.location.host ||
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
    this.loadURL(window.location.href, false).catch(log_error);
  }
}

const router = new Router();
export default router;

/**
 * Sync a store value to the URL.
 *
 * Update and navigate to the URL on store changes.
 */
function syncToURL<T extends boolean | string>(
  store: Writable<T>,
  name: string,
  defaultValue: T,
  shouldLoad = true
): void {
  store.subscribe((val: T) => {
    const newURL = new URL(window.location.href);
    newURL.searchParams.set(name, val.toString());
    if (val === "" || val === defaultValue) {
      newURL.searchParams.delete(name);
    }
    if (newURL.href !== window.location.href) {
      router.navigate(newURL.href, shouldLoad);
    }
  });
}

/**
 * Update URL on store changes.
 */
export function syncStoreValuesToURL(): void {
  syncToURL(account_filter, "account", "");
  syncToURL(fql_filter, "filter", "");
  syncToURL(time_filter, "time", "");
  syncToURL(interval, "interval", DEFAULT_INTERVAL);
  syncToURL(conversion, "conversion", "at_cost");
  syncToURL(showCharts, "charts", true, false);
}
