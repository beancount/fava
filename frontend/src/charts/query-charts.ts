import { stratify } from "../lib/tree";
import type { Inventory, QueryResultTable } from "../reports/query/query_table";
import type { ChartContext } from "./context";
import type { HierarchyChart } from "./hierarchy";
import { hierarchy_from_parsed_data } from "./hierarchy";
import type { LineChart } from "./line";
import { balances_from_parsed_data } from "./line";

/** Get the query chart, if possible, from a query result */
export function getQueryChart(
  table: QueryResultTable,
  $chartContext: ChartContext,
): HierarchyChart | LineChart | null {
  const { columns } = table;
  const [first, second] = columns;
  if (!first || !second || columns.length > 2) {
    return null;
  }
  if (first.dtype === "str" && second.dtype === "Inventory") {
    const grouped = (table.rows as [string, Inventory][]).map(
      ([group, inv]) => ({ group, balance: inv.value }),
    );
    const root = stratify(
      grouped,
      (d) => d.group,
      (account, d) => ({ account, balance: d?.balance ?? {} }),
    );
    root.account = "(root)";
    return hierarchy_from_parsed_data(null, root, $chartContext);
  }
  if (first.dtype === "date" && second.dtype === "Inventory") {
    const bals = (table.rows as [Date, Inventory][]).map(([date, inv]) => ({
      date,
      balance: inv.value,
    }));
    return balances_from_parsed_data(null, bals);
  }
  return null;
}
