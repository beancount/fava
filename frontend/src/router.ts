/**
 * Routing
 *
 * Fava intercepts all clicks on links and will in most cases asynchronously
 * load the content of the page and replace the <article> contents with them.
 */

import type { Readable } from "svelte/store";
import { writable } from "svelte/store";

import { handleExtensionPageLoad } from "./extensions";
import { getUrlPath } from "./helpers";
import { assert_is_error } from "./lib/errors";
import { delegate } from "./lib/events";
import { log_error } from "./log";
import type { RenderedReport } from "./reports/route";
import { backend_route, ErrorRoute, type FrontendRoute } from "./reports/route";
import { has_changes, raw_page_title } from "./sidebar/page-title";
import { current_url } from "./stores/url";

/** Whether this is a left-button click without any modifier keys pressed. */
const is_normal_click = (event: MouseEvent) =>
  event.button === 0 &&
  !event.altKey &&
  !event.ctrlKey &&
  !event.metaKey &&
  !event.shiftKey;

/** Whether this is an external link or has the `data-remote` attribute */
const is_external_link = (link: HTMLAnchorElement | SVGAElement) =>
  link.hasAttribute("data-remote") ||
  (link instanceof HTMLAnchorElement &&
    (link.host !== window.location.host || !link.protocol.startsWith("http")));

/**
 * The various query parameters used in Fava.
 */
type FavaQueryParameters =
  | "account"
  | "charts"
  | "conversion"
  | "filter"
  | "interval"
  | "query_string"
  | "time";

/** Set a query parameter, mutating the URL in place. */
export function set_query_param(
  url: URL,
  key: FavaQueryParameters,
  value: string,
): void {
  if (value) {
    url.searchParams.set(key, value);
  } else {
    url.searchParams.delete(key);
  }
}

const is_loading_internal = writable(false);
/** Whether the logo should be spinning to indicate that something is loading. */
export const is_loading: Readable<boolean> = is_loading_internal;

export class Router {
  /** The current URL - internal, should always be accessed by getter/setter. */
  #current: URL;

  /** The <article> element. */
  #article: HTMLElement;

  /** The frontend rendered routes. */
  #frontend_routes: FrontendRoute[] = [];

  /** The currently rendered route. */
  #current_report?: RenderedReport | undefined;

  /**
   * Function to intercept navigation, e.g., when there are unsaved changes.
   *
   * If they return a string, that is displayed to the user in an alert to
   * confirm navigation.
   */
  #interrupt_handlers = new Set<() => string | null>();

  constructor() {
    const article = document.querySelector("article");
    if (!article) {
      throw new Error("<article> element is missing from markup");
    }
    this.#article = article;

    this.#current = new URL(window.location.href);
    current_url.set(this.#current);
  }

  /** The current URL. */
  get current(): URL {
    return this.#current;
  }

  /** Set the current URL. */
  private set current(url: URL) {
    if (this.#current.href !== url.href) {
      this.#current = url;
      current_url.set(url);
    }
  }

  /**
   * Whether an interrupt handler is active like on the editor or import report.
   * Avoid auto-reloading in that case.
   */
  get has_interrupt_handler(): boolean {
    return this.#interrupt_handlers.size > 0;
  }

  /**
   * Add an interrupt handler. Returns a function that removes it.
   * This can be used directly in a Svelte onMount hook.
   */
  add_interrupt_handler(handler: () => string | null): () => void {
    this.#interrupt_handlers.add(handler);

    return () => {
      this.#interrupt_handlers.delete(handler);
    };
  }

  /**
   * Check whether any of the registered interruptHandlers wants to stop
   * navigation.
   */
  #should_interrupt(): string | null {
    for (const handler of this.#interrupt_handlers) {
      const leave_message = handler();
      if (leave_message != null) {
        return leave_message;
      }
    }
    return null;
  }

  /**
   * Render the route for the given URL.
   */
  async #render_route(url: URL, before_render?: () => void): Promise<void> {
    const previous = this.#current_report;
    const relative_path = getUrlPath(url).unwrap();
    const report = relative_path.slice(0, relative_path.indexOf("/"));
    const route =
      this.#frontend_routes.find((r) => r.report === report) ?? backend_route;

    is_loading_internal.set(true);
    try {
      this.#current_report = await route.render(
        this.#article,
        url,
        previous,
        before_render,
      );
    } catch (error: unknown) {
      assert_is_error(error);
      const error_route = new ErrorRoute(error);
      this.#current_report = error_route.render(
        this.#article,
        url,
        previous,
        before_render,
      );
    }
    raw_page_title.set(this.#current_report.title);
    is_loading_internal.set(false);
  }

  #beforeunload = () => (event: BeforeUnloadEvent) => {
    const leave_message = this.#should_interrupt();
    if (leave_message != null) {
      event.preventDefault();
    }
  };

  #popstate = (): void => {
    const target = new URL(window.location.href);
    const { current } = this;
    if (
      target.pathname !== current.pathname ||
      target.search !== current.search
    ) {
      this.#load_url(target).catch(log_error);
    } else {
      this.current = target;
    }
  };

  /*
   * Intercept all clicks on links (<a>) and .navigate() to the link instead.
   *
   * Doesn't intercept if
   *  - a button different from the main button is used,
   *  - a modifier key is pressed,
   *  - the link starts with a hash '#', or
   *  - the link has a `data-remote` attribute.
   */
  #intercept_link_click = (event: PointerEvent, link: Element): void => {
    if (!(link instanceof HTMLAnchorElement || link instanceof SVGAElement)) {
      return;
    }
    if (!is_normal_click(event)) {
      return;
    }
    if (event.defaultPrevented) {
      return;
    }
    if (link.getAttribute("href")?.charAt(0) === "#") {
      return;
    }
    if (is_external_link(link)) {
      return;
    }

    event.preventDefault();
    const href =
      link instanceof HTMLAnchorElement ? link.href : link.href.baseVal;

    this.navigate(href);
  };

  /**
   * This should be called once when the page has been loaded. Initializes the
   * router and takes over clicking on links.
   */
  init(frontend_routes: FrontendRoute[]): void {
    this.#frontend_routes = frontend_routes;
    this.#render_route(this.current).catch(log_error);

    window.addEventListener("beforeunload", this.#beforeunload);
    window.addEventListener("popstate", this.#popstate);
    delegate(document, "click", "a", this.#intercept_link_click);

    handleExtensionPageLoad();
  }

  /**
   * Go to URL.
   *
   * If load is `true`, load the page at URL, otherwise only push
   * a new history item update and update the current url.
   */
  navigate(url: string | URL, load = true): void {
    const target =
      url instanceof URL ? url : new URL(url, window.location.href);
    if (load) {
      this.#load_url(target).catch(log_error);
    } else {
      window.history.pushState(null, "", target);
      this.current = target;
    }
  }

  /**
   * Replace `<article>` contents with the page at `url`.
   *
   * Might render in the frontend or load the whole page contents.
   */
  async #load_url(url: URL): Promise<void> {
    const leave_message = this.#should_interrupt();
    if (leave_message != null && !window.confirm(leave_message)) {
      return;
    }

    const is_reload = url.href === this.current.href;
    const before_render = is_reload
      ? undefined
      : () => {
          // Push state and set current URL after loading the data but before rendering.
          this.#article.scroll(0, 0);
          if (url.href !== window.location.href) {
            window.history.pushState(null, "", url);
          }
          this.current = url;
        };
    await this.#render_route(url, before_render);

    has_changes.set(false);
    handleExtensionPageLoad();

    const hash = this.current.hash.slice(1);
    if (hash) {
      document.getElementById(hash)?.scrollIntoView();
    }
  }

  /**
   * Set the URL parameter and push a history state for it if changed.
   *
   * For `charts` and `query_string`, this will not load the target URL.
   */
  set_search_param(key: "charts", value: "false" | ""): void;
  set_search_param(
    key:
      | "account"
      | "conversion"
      | "filter"
      | "interval"
      | "query_string"
      | "time",
    value: string,
  ): void;
  set_search_param(key: FavaQueryParameters, value: string): void {
    const target = new URL(this.current);
    set_query_param(target, key, value);
    if (target.href !== this.current.href) {
      const load = !(key === "charts" || key === "query_string");
      this.navigate(target, load);
    }
  }

  /**
   * Close the modal overlay.
   */
  close_overlay = (): void => {
    if (this.current.hash) {
      const target = new URL(this.current);
      target.hash = "";
      this.navigate(target, false);
    }
  };

  /*
   * Reload the page.
   */
  reload = (): void => {
    this.#load_url(this.current).catch(log_error);
  };
}

/** The Fava router. */
export const router = new Router();
