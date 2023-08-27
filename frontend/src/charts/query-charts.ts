import type { Result } from "../lib/result";
import { stratify } from "../lib/tree";
import { array, number, object, record, string } from "../lib/validation";

import type { ChartContext } from "./context";
import type { HierarchyChart } from "./hierarchy";
import { hierarchy_from_parsed_data } from "./hierarchy";
import type { LineChart } from "./line";
import { balances } from "./line";

const grouped_chart_validator = array(
  object({ group: string, balance: record(number) }),
);

export function parseGroupedQueryChart(
  json: unknown,
  $chartContext: ChartContext,
): Result<HierarchyChart, string> {
  return grouped_chart_validator(json)
    .map_err(() => "No grouped query data")
    .map((grouped) => {
      const root = stratify(
        grouped,
        (d) => d.group,
        (account, d) => ({ account, balance: d?.balance ?? {} }),
      );
      root.account = "(root)";
      return hierarchy_from_parsed_data(null, root, $chartContext);
    });
}

/**
 * Parse one of the query result charts.
 * @param json - The chart data to parse.
 */
export function parseQueryChart(
  json: unknown,
  $chartContext: ChartContext,
): Result<HierarchyChart | LineChart, string> {
  return (
    parseGroupedQueryChart(json, $chartContext)
      // Try balances chart if the grouped chart parse
      .or_else(() => balances(null, json))
      .map_err(() => "No query chart found.")
  );
}
