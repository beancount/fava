import { _ } from "../i18n";
import { account_report } from "./accounts";
import { commodities } from "./commodities";
import { documents } from "./documents";
import { editor } from "./editor";
import ErrorsSvelte from "./errors/Errors.svelte";
import { events } from "./events";
import { holdings } from "./holdings";
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
  documents,
  editor,
  new Route("errors", ErrorsSvelte, noload, () => _("Errors")),
  events,
  holdings,
  import_report,
  income_statement,
  new Route("query", QuerySvelte, noload, () => _("Query")),
  trial_balance,
];
