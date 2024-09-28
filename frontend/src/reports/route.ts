import type { SvelteComponent } from "svelte";

import { log_error } from "../log";
import ErrorSvelte from "./Error.svelte";

/** This class pairs the components and their load functions to use them in a type-safe way. */
export class Route<
  T extends Record<string, unknown> = Record<string, unknown>,
> {
  /** The currently rendered instance - if loading failed, we render an error component. */
  private instance?:
    | { error: false; component: SvelteComponent<T> }
    | { error: true; component: ErrorSvelte };

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
    private readonly Component: typeof SvelteComponent<T>,
    private readonly load: (url: URL) => T | Promise<T>,
    private readonly get_title: (route: Route) => string,
  ) {}

  /** The title of this report. */
  get title(): string {
    return this.get_title(this);
  }

  /** Destroy any components that might be rendered by this route. */
  destroy(): void {
    this.instance?.component.$destroy();
    this.instance = undefined;
  }

  /** Load data and render the component for this route to the given target. */
  async render(target: HTMLElement, url: URL, previous?: Route): Promise<void> {
    if (previous !== this) {
      previous?.destroy();
    }
    try {
      const props = await this.load(url);
      // Check if the component is changed - otherwise only update the data.
      if (previous === this && this.instance?.error === false) {
        this.instance.component.$set(props);
      } else {
        this.destroy();
        target.innerHTML = "";
        this.instance = {
          error: false,
          component: new this.Component({ target, props }),
        };
      }
    } catch (error: unknown) {
      log_error(error);
      if (error instanceof Error) {
        this.destroy();
        target.innerHTML = "";
        this.instance = {
          error: true,
          component: new ErrorSvelte({
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
