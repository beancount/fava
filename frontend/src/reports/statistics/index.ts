import { get_query, get_statistics } from "../../api/index.ts";
import { _ } from "../../i18n.ts";
import { getURLFilters } from "../../stores/filters.ts";
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
  async (url) => {
    const postings_per_account = await get_query({
      query_string: postings_per_account_query,
      ...getURLFilters(url),
    });
    const { all_balance_directives, balances, entries_by_type } =
      await get_statistics(getURLFilters(url));
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
