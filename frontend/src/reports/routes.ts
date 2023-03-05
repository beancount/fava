import type { SvelteComponent } from "svelte";
import { get } from "svelte/store";

import { _ } from "../i18n";
import { base_url } from "../stores";

import CommoditiesSvelte from "./commodities/Commodities.svelte";
import { load as load_commodities } from "./commodities/load";
import DocumentsSvelte from "./documents/Documents.svelte";
import { load as load_documents } from "./documents/load";
import EditorSvelte from "./editor/Editor.svelte";
import { load as load_editor } from "./editor/load";
import ErrorsSvelte from "./errors/Errors.svelte";
import EventsSvelte from "./events/Events.svelte";
import { load as load_events } from "./events/load";
import ImportSvelte from "./import/Import.svelte";
import { load as load_import } from "./import/load";
import QuerySvelte from "./query/Query.svelte";

/** A svelte component to render a Fava report in the frontend. */
export type FrontendComponent = typeof SvelteComponent;

type LoadFunction = (url: URL) => Promise<unknown>;

const noload = () => Promise.resolve(null);

/**
 * This is a list of routes to render in the frontend. For those that we render
 * in the frontend, the router will pre-load any required data with the load
 * function and then render the component. These components hence need to be
 * able to react to changed data (using idiomatic Svelte code should ensure
 * that, care mainly needs to be taken around lifecycle hooks that should run
 * if some parts of the data change)
 */
const routes: [
  report: string,
  Cls: FrontendComponent,
  load: LoadFunction,
  title: () => string
][] = [
  ["commodities", CommoditiesSvelte, load_commodities, () => _("Commodities")],
  ["documents", DocumentsSvelte, load_documents, () => _("Documents")],
  ["editor", EditorSvelte, load_editor, () => _("Editor")],
  ["errors", ErrorsSvelte, noload, () => _("Errors")],
  ["events", EventsSvelte, load_events, () => _("Events")],
  ["import", ImportSvelte, load_import, () => _("Import")],
  ["query", QuerySvelte, noload, () => _("Query")],
];

export function shouldRenderInFrontend(
  url: Pick<URL, "pathname">
): [Cls: FrontendComponent, load: LoadFunction, title: string] | null {
  const base_url_val = get(base_url);
  if (base_url_val && url.pathname.startsWith(base_url_val)) {
    const report = url.pathname.slice(base_url_val.length);
    for (const route of routes) {
      const [rep, Cls, load, title_getter] = route;
      if (report === `${rep}/`) {
        return [Cls, load, title_getter()];
      }
    }
  }
  return null;
}

export type GetFrontendComponent = typeof shouldRenderInFrontend;
