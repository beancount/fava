import type { SvelteComponent } from "svelte";
import { get } from "svelte/store";

import { _ } from "../i18n";
import { base_url } from "../stores";

import CommoditiesSvelte from "./commodities/Commodities.svelte";
import DocumentsAsyncSvelte from "./documents/DocumentsAsync.svelte";
import EditorSvelte from "./editor/Editor.svelte";
import EventsSvelte from "./events/Events.svelte";
import ImportAsync from "./import/ImportAsync.svelte";
import QuerySvelte from "./query/Query.svelte";

/** A svelte component to render a Fava report in the frontend. */
export type FrontendComponent = typeof SvelteComponent;

const routes: [report: string, Cls: FrontendComponent, title: () => string][] =
  [
    ["commodities", CommoditiesSvelte, () => _("Commodities")],
    ["documents", DocumentsAsyncSvelte, () => _("Documents")],
    ["editor", EditorSvelte, () => _("Editor")],
    ["events", EventsSvelte, () => _("Events")],
    ["import", ImportAsync, () => _("Import")],
    ["query", QuerySvelte, () => _("Query")],
  ];

export function shouldRenderInFrontend(
  url: Pick<URL, "pathname">
): [Cls: FrontendComponent, title: string] | null {
  const base_url_val = get(base_url);
  if (base_url_val && url.pathname.startsWith(base_url_val)) {
    const report = url.pathname.slice(base_url_val.length);
    for (const route of routes) {
      const [rep, Cls, title_getter] = route;
      if (report === `${rep}/`) {
        return [Cls, title_getter()];
      }
    }
  }
  return null;
}

export type GetFrontendComponent = typeof shouldRenderInFrontend;
