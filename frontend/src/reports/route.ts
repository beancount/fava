import { type Component, mount, unmount } from "svelte";

import { _ } from "../i18n.ts";
import { getScriptTagValue } from "../lib/dom.ts";
import { fetch_text } from "../lib/fetch.ts";
import { string } from "../lib/validation.ts";
import { read_mtime } from "../stores/mtime.ts";
import ReportLoadError from "./ReportLoadError.svelte";
import { updateable_props } from "./route.svelte.ts";

export interface BaseRoute {
  /** Load data and render the component for this route to the given target. */
  render(
    target: HTMLElement,
    url: URL,
    previous?: RenderedReport,
    before_render?: () => void,
  ): RenderedReport | Promise<RenderedReport>;
}

export class RenderedReport {
  readonly route: BaseRoute;
  readonly url: URL;
  readonly title: string;
  readonly destroy: () => void;

  /**
   * A succesfully rendered report.
   * @param route - The route that is rendered.
   * @param url - The URL that is rendered.
   * @param title - The title for this report.
   */
  constructor(route: BaseRoute, url: URL, title: string, destroy: () => void) {
    this.route = route;
    this.url = url;
    this.title = title;
    this.destroy = destroy;
  }
}

class BackendRenderedReport extends RenderedReport {
  constructor(route: BaseRoute, url: URL, target: HTMLElement) {
    const title = getScriptTagValue("#page-title", string).unwrap_or(
      "ERROR: reading #page-title failed.",
    );
    super(route, url, title, () => {
      target.innerHTML = "";
    });
  }
}

/**
 * Load HTML for a report that is rendered in the backend.
 */
class BackendRoute implements BaseRoute {
  async render(
    target: HTMLElement,
    url: URL,
    previous?: RenderedReport,
    before_render?: () => void,
  ): Promise<RenderedReport> {
    if (previous == null) {
      // Nothing to do on the first render.
      return new BackendRenderedReport(this, url, target);
    }
    const get_url = new URL(url);
    get_url.searchParams.set("partial", "true");
    const content = await fetch_text(get_url);
    if (previous.route !== this) {
      previous.destroy();
    }
    before_render?.();
    target.innerHTML = content;
    read_mtime();

    return new BackendRenderedReport(this, url, target);
  }
}

/**
 * Render an error message.
 */
export class ErrorRoute implements BaseRoute {
  private readonly error: Error;

  constructor(error: Error) {
    this.error = error;
  }

  render(
    target: HTMLElement,
    url: URL,
    previous?: RenderedReport,
    before_render?: () => void,
  ): RenderedReport {
    previous?.destroy();
    before_render?.();
    const instance = mount(ReportLoadError, {
      target,
      props: { title: url.pathname, error: this.error },
    });
    return new RenderedReport(this, url, _("Error"), () => {
      void unmount(instance);
    });
  }
}

export const backend_route = new BackendRoute();

export interface FrontendRoute extends BaseRoute {
  /** URL slug of this report. */
  readonly report: string;
}

/** This class pairs the components and their load functions to use them in a type-safe way. */
// The base type for the component props needs to be typed as Record<string,any> to allow for T
// to be correctly inferred from the imported svelte components
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export class Route<T extends Record<string, any>> implements FrontendRoute {
  readonly report: string;
  private readonly Component: Component<T>;
  private readonly load: (url: URL) => T | Promise<T>;
  readonly get_title: (url: URL) => string;
  /** The currently rendered instance - if loading failed, we render an error component. */
  private instance?:
    | {
        component: Record<string, unknown>;
        update_props: (v: T) => void;
      }
    | undefined;

  /**
   * Create a new frontend-rendered route.
   * @param report URL slug of this report.
   * @param Component the component to render for this report.
   * @param load function to load the necessary data.
   * @param get_title function to get the page title.
   */
  constructor(
    report: string,
    Component: Component<T>,
    load: (url: URL) => T | Promise<T>,
    get_title: (url: URL) => string,
  ) {
    this.report = report;
    this.Component = Component;
    this.load = load;
    this.get_title = get_title;
  }

  async render(
    target: HTMLElement,
    url: URL,
    previous?: RenderedReport,
    before_render?: () => void,
  ): Promise<RenderedReport> {
    const raw_props = await this.load(url);
    if (previous?.route !== this) {
      previous?.destroy();
    }
    before_render?.();
    if (previous?.route === this && this.instance != null) {
      // Check if the component is unchanged and only update the data in this case.
      this.instance.update_props(raw_props);
    } else {
      previous?.destroy();
      const [props, update_props] = updateable_props(raw_props);
      this.instance = {
        component: mount(this.Component, { target, props }),
        update_props,
      };
    }
    return new RenderedReport(this, url, this.get_title(url), () => {
      if (this.instance) {
        void unmount(this.instance.component);
      }
      this.instance = undefined;
    });
  }
}

type NoProps = Record<string, never>;

const noload = () => ({});

/** A frontend rendered route that does not need to load any props. */
export class DatalessRoute extends Route<NoProps> {
  constructor(
    report: string,
    Component: Component<NoProps>,
    get_title: (url: URL) => string,
  ) {
    super(report, Component, noload, get_title);
  }
}
