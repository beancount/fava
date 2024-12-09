import { get } from "../../api";
import { getUrlPath } from "../../helpers";
import { _ } from "../../i18n";
import { getURLFilters } from "../../stores/filters";
import { Route } from "../route";
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

const QUERIES = {
  all: `
SELECT
  account,
  units(sum(position)) as units,
  cost_number as cost,
  first(getprice(currency, cost_currency)) as price,
  cost(sum(position)) as book_value,
  value(sum(position)) as market_value,
  safediv((abs(sum(number(value(position)))) - abs(sum(number(cost(position))))), sum(number(cost(position)))) * 100 as unrealized_profit_pct,
  cost_date as acquisition_date
WHERE account_sortkey(account) ~ "^[01]"
GROUP BY account, cost_date, currency, cost_currency, cost_number, account_sortkey(account)
ORDER BY account_sortkey(account), currency, cost_date
`.trim(),
  by_account: `
SELECT
  account,
  units(sum(position)) as units,
  cost(sum(position)) as book_value,
  value(sum(position)) as market_value,
  safediv((abs(sum(number(value(position)))) - abs(sum(number(cost(position))))), sum(number(cost(position)))) * 100 as unrealized_profit_pct
WHERE account_sortkey(account) ~ "^[01]"
GROUP BY account, cost_currency, account_sortkey(account), currency
ORDER BY account_sortkey(account), currency
`.trim(),
  by_currency: `
SELECT
  units(sum(position)) as units,
  safediv(number(only(first(cost_currency), cost(sum(position)))), number(only(first(currency), units(sum(position))))) as average_cost,
  first(getprice(currency, cost_currency)) as price,
  cost(sum(position)) as book_value,
  value(sum(position)) as market_value,
  safediv((abs(sum(number(value(position)))) - abs(sum(number(cost(position))))), sum(number(cost(position)))) * 100 as unrealized_profit_pct
WHERE account_sortkey(account) ~ "^[01]"
GROUP BY currency, cost_currency
ORDER BY currency, cost_currency
`.trim(),
  by_cost_currency: `
SELECT
  units(sum(position)) as units,
  cost(sum(position)) as book_value,
  value(sum(position)) as market_value,
  safediv((abs(sum(number(value(position)))) - abs(sum(number(cost(position))))), sum(number(cost(position)))) * 100 as unrealized_profit_pct
WHERE account_sortkey(account) ~ "^[01]"
GROUP BY cost_currency
ORDER BY cost_currency
`.trim(),
};

export const holdings = new Route(
  "holdings",
  Holdings,
  async (url) => {
    const [, key = ""] = getUrlPath(url)?.split("/") ?? [];
    const aggregation_key = to_report_type(key);
    const query_string = QUERIES[aggregation_key];
    const query_result_table = await get("query", {
      query_string,
      ...getURLFilters(url),
    });
    if (query_result_table.t !== "table") {
      throw new Error("Internal error: expected a query result table");
    }
    return { aggregation_key, query_string, query_result_table };
  },
  () => _("Holdings"),
);
