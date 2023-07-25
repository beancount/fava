import { hierarchy as d3Hierarchy } from "d3-hierarchy";

import type { Result } from "../lib/result";
import { stratify } from "../lib/tree";
import { array, number, object, record, string } from "../lib/validation";

import type { ChartContext } from "./context";
import type { AccountHierarchyDatum, AccountHierarchyNode } from "./hierarchy";
import { HierarchyChart } from "./hierarchy";
import type { LineChart } from "./line";
import { balances } from "./line";

const grouped_chart_validator = array(
  object({ group: string, balance: record(number) }),
);

export function parseGroupedQueryChart(
  json: unknown,
  { currencies }: ChartContext,
): Result<HierarchyChart, string> {
  return grouped_chart_validator(json)
    .map_err(() => "No grouped query data")
    .map((grouped) => {
      const root: AccountHierarchyDatum = stratify(
        grouped,
        (d) => d.group,
        (account, d) => ({ account, balance: d?.balance ?? {} }),
      );
      root.account = "(root)";

      const data = new Map<string, AccountHierarchyNode>();
      currencies.forEach((currency) => {
        const currencyHierarchy = d3Hierarchy(root)
          .sum((d) => d.balance[currency] ?? 0)
          .sort((a, b) => (b.value ?? 0) - (a.value ?? 0));
        if (currencyHierarchy.value !== undefined) {
          data.set(currency, currencyHierarchy);
        }
      });

      return new HierarchyChart(null, data);
    });
}

/**
 * Parse one of the query result charts.
 * @param json - The chart data to parse.
 */
export function parseQueryChart(
  json: unknown,
  ctx: ChartContext,
): Result<HierarchyChart | LineChart, string> {
  return (
    parseGroupedQueryChart(json, ctx)
      // Try balances chart if the grouped chart parse
      .or_else(() => balances(null, json))
      .map_err(() => "No query chart found.")
  );
}
