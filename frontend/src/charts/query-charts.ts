import { hierarchy as d3Hierarchy } from "d3-hierarchy";

import { err, ok } from "../lib/result";
import type { Result } from "../lib/result";
import { stratify } from "../lib/tree";
import {
  array,
  number,
  object,
  record,
  string,
  unknown,
} from "../lib/validation";

import type { ChartContext } from "./context";
import type {
  AccountHierarchyDatum,
  AccountHierarchyNode,
  HierarchyChart,
} from "./hierarchy";
import { balances } from "./line";

import type { FavaChart } from "./index";

const grouped_chart_validator = array(
  object({ group: string, balance: record(number) })
);
export function parseGroupedQueryChart(
  json: unknown,
  { currencies }: ChartContext
): Result<HierarchyChart, string> {
  const grouped = grouped_chart_validator(json);
  if (!grouped.success) {
    return err("No grouped query data");
  }
  const root: AccountHierarchyDatum = stratify(
    grouped.value,
    (d) => d.group,
    (account, d) => ({ account, balance: d?.balance ?? {} })
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

  return ok({ type: "hierarchy" as const, data });
}

/**
 * Parse one of the query result charts.
 * @param json - The chart data to parse.
 */
export function parseQueryChart(
  json: unknown,
  ctx: ChartContext
): Result<FavaChart, string> {
  const tree = parseGroupedQueryChart(json, ctx);
  if (tree.success) {
    return tree;
  }
  const dated = array(unknown)(json);
  if (dated.success) {
    const bal = balances(dated.value);
    if (bal.success) {
      return bal;
    }
  }
  return err("No query chart found.");
}
