import type { SvelteComponent } from "svelte";

import { getUrlPath } from "../helpers";
import { _ } from "../i18n";
import { log_error } from "../log";

import CommoditiesSvelte from "./commodities/Commodities.svelte";
import { load as load_commodities } from "./commodities/load";
import DocumentsSvelte from "./documents/Documents.svelte";
import { load as load_documents } from "./documents/load";
import EditorSvelte from "./editor/Editor.svelte";
import { load as load_editor } from "./editor/load";
import ErrorSvelte from "./Error.svelte";
import ErrorsSvelte from "./errors/Errors.svelte";
import EventsSvelte from "./events/Events.svelte";
import { load as load_events } from "./events/load";
import ImportSvelte from "./import/Import.svelte";
import { load as load_import } from "./import/load";
import QuerySvelte from "./query/Query.svelte";

/** This class pairs the components and their load functions to use them in a type-safe way. */
export class Route<
  T extends Record<string, unknown> = Record<string, unknown>
> {
  /** The currently rendered instance - if loading failed, we render an error component. */
  private instance?:
    | { error: false; component: SvelteComponent<T> }
    | { error: true; component: ErrorSvelte };

  constructor(
    readonly report: string,
    private readonly Component: typeof SvelteComponent<T>,
    private readonly load: (url: URL) => Promise<T>,
    private readonly get_title: () => string
  ) {}

  /** The title of this report. */
  get title() {
    return this.get_title();
  }

  /** Destroy any components that might be rendered by this route. */
  destroy() {
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
    }
  }
}

const noload = () => Promise.resolve({});

/**
 * This is a list of routes to render in the frontend. For those that we render
 * in the frontend, the router will pre-load any required data with the load
 * function and then render the component. These components hence need to be
 * able to react to changed data (using idiomatic Svelte code should ensure
 * that, care mainly needs to be taken around lifecycle hooks that should run
 * if some parts of the data change)
 */
export const frontend_routes: Route[] = [
  new Route("commodities", CommoditiesSvelte, load_commodities, () =>
    _("Commodities")
  ),
  new Route("documents", DocumentsSvelte, load_documents, () => _("Documents")),
  new Route("editor", EditorSvelte, load_editor, () => _("Editor")),
  new Route("errors", ErrorsSvelte, noload, () => _("Errors")),
  new Route("events", EventsSvelte, load_events, () => _("Events")),
  new Route("import", ImportSvelte, load_import, () => _("Import")),
  new Route("query", QuerySvelte, noload, () => _("Query")),
];

/** Find the `Route` to render this url with if it matches one of the routes. */
export function shouldRenderInFrontend(url: URL): Route | undefined {
  const report = getUrlPath(url);
  return frontend_routes.find((route) => report === `${route.report}/`);
}
