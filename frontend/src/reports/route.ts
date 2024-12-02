import { type Component, mount, unmount } from "svelte";

import { log_error } from "../log";
import ErrorSvelte from "./Error.svelte";
import { updateable_props } from "./route.svelte";

export interface FrontendRoute {
  readonly report: string;
  readonly title: string;
  destroy(): void;
  render(
    target: HTMLElement,
    url: URL,
    previous?: FrontendRoute,
  ): Promise<void>;
}

/** This class pairs the components and their load functions to use them in a type-safe way. */
// The base type for the component props needs to be typed as Record<string,any> to allow for T
// to be correctly inferred from the imported svelte components
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export class Route<T extends Record<string, any>> implements FrontendRoute {
  /** The currently rendered instance - if loading failed, we render an error component. */
  private instance?:
    | {
        error: false;
        component: Record<string, unknown>;
        update_props: (v: T) => void;
      }
    | { error: true; component: Record<string, unknown> };

  /** The currently rendered URL. */
  url?: URL;

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
    private readonly get_title: (route: Route<T>) => string,
  ) {}

  /** The title of this report. */
  get title(): string {
    return this.get_title(this);
  }

  /** Destroy any components that might be rendered by this route. */
  destroy(): void {
    if (this.instance !== undefined) {
      void unmount(this.instance.component);
    }
    this.instance = undefined;
  }

  /** Load data and render the component for this route to the given target. */
  async render(
    target: HTMLElement,
    url: URL,
    previous?: FrontendRoute,
  ): Promise<void> {
    if (previous !== this) {
      previous?.destroy();
    }
    try {
      const raw_props = await this.load(url);
      // Check if the component is unchanged and only update the data in this case.
      if (previous === this && this.instance?.error === false) {
        this.instance.update_props(raw_props);
      } else {
        this.destroy();
        target.innerHTML = "";
        const [props, update_props] = updateable_props(raw_props);
        this.instance = {
          error: false,
          component: mount(this.Component, { target, props }),
          update_props,
        };
      }
    } catch (error: unknown) {
      log_error(error);
      if (error instanceof Error) {
        this.destroy();
        target.innerHTML = "";
        this.instance = {
          error: true,
          component: mount(ErrorSvelte, {
            target,
            props: { title: this.title, error },
          }),
        };
      }
    } finally {
      this.url = url;
    }
  }
}

export const noload = (): Record<string, unknown> => ({});
