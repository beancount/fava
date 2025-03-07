import { account_report } from "./accounts";
import { commodities } from "./commodities";
import { documents } from "./documents";
import { editor } from "./editor";
import { errors } from "./errors";
import { events } from "./events";
import { holdings } from "./holdings";
import { import_report } from "./import";
import { options } from "./options";
import { query } from "./query";
import type { FrontendRoute } from "./route";
import { balance_sheet, income_statement, trial_balance } from "./tree_reports";

/**
 * This is a list of routes to render in the frontend. For those that we render
 * in the frontend, the router will pre-load any required data with the load
 * function and then render the component. These components hence need to be
 * able to react to changed data (using idiomatic Svelte code should ensure
 * that, care mainly needs to be taken around lifecycle hooks that should run
 * if some parts of the data change)
 */
export const frontend_routes: FrontendRoute[] = [
  account_report,
  balance_sheet,
  commodities,
  documents,
  editor,
  errors,
  events,
  holdings,
  import_report,
  income_statement,
  options,
  query,
  trial_balance,
];
