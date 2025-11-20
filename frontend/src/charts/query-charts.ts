import { stratify } from "../lib/tree.ts";
import type {
  Inventory,
  QueryResultTable,
} from "../reports/query/query_table.ts";
import type { ChartContext } from "./context.ts";
import type { HierarchyChart } from "./hierarchy.ts";
import { ParsedHierarchyChart } from "./hierarchy.ts";
import type { LineChart } from "./line.ts";
import { ParsedLineChart } from "./line.ts";

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
    return new ParsedHierarchyChart(null, root).with_context($chartContext);
  }
  if (first.dtype === "date" && second.dtype === "Inventory") {
    const bals = (table.rows as [Date, Inventory][]).map(([date, inv]) => ({
      date,
      balance: inv.value,
    }));
    return new ParsedLineChart(null, bals).with_context();
  }
  return null;
}
