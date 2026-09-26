import { get_holdings } from "../../api/index.ts";
import { get_url_path } from "../../helpers.ts";
import { _ } from "../../i18n.ts";
import { get_url_filters } from "../../stores/filters.ts";
import type { QueryResultTable } from "../query/query_table.ts";
import { Route } from "../route.ts";
import Holdings from "./Holdings.svelte";

export type HoldingsReportType =
  | "all"
  | "by_account"
  | "by_currency"
  | "by_cost_currency";

const to_report_type = (s: string | null): HoldingsReportType =>
  s === "by_account" || s === "by_currency" || s === "by_cost_currency"
    ? s
    : "all";

export interface HoldingsReportProps {
  aggregation_key: HoldingsReportType;
  query_string: string;
  query_result_table: QueryResultTable;
}

export const holdings = new Route<HoldingsReportProps>(
  "holdings",
  Holdings,
  async (url) => {
    const [, key = ""] = get_url_path(url).unwrap().split("/");
    const aggregation_key = to_report_type(key);
    const { query_string, query_result_table } = await get_holdings({
      aggregation_key,
      ...get_url_filters(url),
    });
    if (query_result_table.t !== "table") {
      throw new Error("Internal error: expected a query result table");
    }
    return { aggregation_key, query_string, query_result_table };
  },
  () => _("Holdings"),
);
