import { type Component, mount, unmount } from "svelte";

import { _ } from "../i18n";
import { getScriptTagValue } from "../lib/dom";
import { fetch, handleText } from "../lib/fetch";
import { string } from "../lib/validation";
import ReportLoadError from "./ReportLoadError.svelte";
import { updateable_props } from "./route.svelte";

export interface BaseRoute {
  /** The title of this report. */
  get_title(url: URL): string;

  /** Destroy any components that might be rendered by this route. */
  destroy(): void;

  /** Load data and render the component for this route to the given target. */
  render(
    target: HTMLElement,
    url: URL,
    previous?: BaseRoute,
    before_render?: () => void,
  ): void | Promise<void>;
}

/**
 * Load HTML for a report that is rendered in the backend.
 */
class BackendRoute implements BaseRoute {
  target: HTMLElement | undefined;

  get_title(): string {
    return getScriptTagValue("#page-title", string).unwrap_or(
      "ERROR: reading #page-title failed.",
    );
  }

  destroy(): void {
    if (this.target) {
      this.target.innerHTML = "";
    }
    this.target = undefined;
  }

  async render(
    target: HTMLElement,
    url: URL,
    previous?: BaseRoute,
    before_render?: () => void,
  ): Promise<void> {
    this.target = target;
    if (previous == null) {
      // Nothing to do on the first render.
      return;
    }
    const get_url = new URL(url);
    get_url.searchParams.set("partial", "true");
    const content = await fetch(get_url).then(handleText);
    if (previous !== this) {
      previous.destroy();
    }
    before_render?.();
    target.innerHTML = content;
  }
}

/**
 * Render an error message.
 */
export class ErrorRoute implements BaseRoute {
  private instance?: Record<string, unknown> | undefined;

  constructor(private readonly error: Error) {}

  get_title(): string {
    return _("Error");
  }

  destroy(): void {
    if (this.instance) {
      void unmount(this.instance);
    }
    this.instance = undefined;
  }

  render(
    target: HTMLElement,
    url: URL,
    previous?: BaseRoute,
    before_render?: () => void,
  ): void {
    previous?.destroy();
    before_render?.();
    this.instance = mount(ReportLoadError, {
      target,
      props: { title: url.pathname, error: this.error },
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
    readonly report: string,
    private readonly Component: Component<T>,
    private readonly load: (url: URL) => T | Promise<T>,
    readonly get_title: (url: URL) => string,
  ) {}

  destroy(): void {
    if (this.instance) {
      void unmount(this.instance.component);
    }
    this.instance = undefined;
  }

  async render(
    target: HTMLElement,
    url: URL,
    previous?: BaseRoute,
    before_render?: () => void,
  ): Promise<void> {
    const raw_props = await this.load(url);
    if (previous !== this) {
      previous?.destroy();
    }
    before_render?.();
    if (previous === this && this.instance != null) {
      // Check if the component is unchanged and only update the data in this case.
      this.instance.update_props(raw_props);
    } else {
      this.destroy();
      const [props, update_props] = updateable_props(raw_props);
      this.instance = {
        component: mount(this.Component, { target, props }),
        update_props,
      };
    }
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
