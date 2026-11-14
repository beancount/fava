import { get_query, get_statistics } from "../../api/index.ts";
import { _ } from "../../i18n.ts";
import { get_url_filters } from "../../stores/filters.ts";
import type { Inventory, QueryResultTable } from "../query/query_table.ts";
import { Route } from "../route.ts";
import Statistics from "./Statistics.svelte";

export interface StatisticsReportProps {
  all_balance_directives: string;
  balances: Record<string, Inventory>;
  entries_by_type: Record<string, number>;
  postings_per_account: QueryResultTable;
}
export const postings_per_account_query =
  "SELECT account, count(account) ORDER BY account";

export const statistics = new Route<StatisticsReportProps>(
  "statistics",
  Statistics,
  async (url, signal) => {
    const filters = get_url_filters(url);
    const [
      postings_per_account,
      { all_balance_directives, balances, entries_by_type },
    ] = await Promise.all([
      get_query(
        { query_string: postings_per_account_query, ...filters },
        signal,
      ),
      get_statistics(filters, signal),
    ]);
    if (postings_per_account.t !== "table") {
      throw new Error("Internal error: expected a query result table");
    }
    return {
      all_balance_directives,
      balances,
      entries_by_type,
      postings_per_account,
    };
  },
  () => _("Statistics"),
);
