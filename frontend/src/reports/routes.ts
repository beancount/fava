import { getUrlPath } from "../helpers";
import { _ } from "../i18n";

import { account_report } from "./accounts";
import { commodities } from "./commodities";
import DocumentsSvelte from "./documents/Documents.svelte";
import { load as load_documents } from "./documents/load";
import EditorSvelte from "./editor/Editor.svelte";
import { load as load_editor } from "./editor/load";
import ErrorsSvelte from "./errors/Errors.svelte";
import EventsSvelte from "./events/Events.svelte";
import { load as load_events } from "./events/load";
import { import_report } from "./import";
import QuerySvelte from "./query/Query.svelte";
import { noload, Route } from "./route";
import { balance_sheet, income_statement, trial_balance } from "./tree_reports";

/**
 * This is a list of routes to render in the frontend. For those that we render
 * in the frontend, the router will pre-load any required data with the load
 * function and then render the component. These components hence need to be
 * able to react to changed data (using idiomatic Svelte code should ensure
 * that, care mainly needs to be taken around lifecycle hooks that should run
 * if some parts of the data change)
 */
export const frontend_routes: Route[] = [
  account_report,
  balance_sheet,
  commodities,
  new Route("documents", DocumentsSvelte, load_documents, () => _("Documents")),
  new Route("editor", EditorSvelte, load_editor, () => _("Editor")),
  new Route("errors", ErrorsSvelte, noload, () => _("Errors")),
  new Route("events", EventsSvelte, load_events, () => _("Events")),
  import_report,
  income_statement,
  new Route("query", QuerySvelte, noload, () => _("Query")),
  trial_balance,
];

/** Find the `Route` to render this url with if it matches one of the routes. */
export function shouldRenderInFrontend(url: URL): Route | undefined {
  const report = getUrlPath(url);
  return frontend_routes.find(
    (route) => report?.startsWith(`${route.report}/`),
  );
}
