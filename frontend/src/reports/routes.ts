import { account_report } from "./accounts/index.ts";
import { commodities } from "./commodities/index.ts";
import { documents } from "./documents/index.ts";
import { editor } from "./editor/index.ts";
import { errors } from "./errors/index.ts";
import { events } from "./events/index.ts";
import { holdings } from "./holdings/index.ts";
import { import_report } from "./import/index.ts";
import { journal } from "./journal/index.ts";
import { options } from "./options/index.ts";
import { query } from "./query/index.ts";
import type { FrontendRoute } from "./route.ts";
import { statistics } from "./statistics/index.ts";
import {
  balance_sheet,
  income_statement,
  trial_balance,
} from "./tree_reports/index.ts";

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
  journal,
  options,
  query,
  statistics,
  trial_balance,
];
