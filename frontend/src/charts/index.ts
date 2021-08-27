/**
 * This module contains the main code to render Fava's charts.
 *
 * The charts heavily use d3 libraries.
 */

import type { HierarchyNode } from "d3-hierarchy";
import { hierarchy as d3Hierarchy } from "d3-hierarchy";
import { get } from "svelte/store";

import type { FormatterContext } from "../format";
import { currentDateFormat, dateFormat } from "../format";
import { getScriptTagJSON } from "../lib/dom";
import type { Result } from "../lib/result";
import { err, ok } from "../lib/result";
import type { TreeNode } from "../lib/tree";
import { stratify } from "../lib/tree";
import type { Validator } from "../lib/validation";
import {
  array,
  date,
  lazy,
  number,
  object,
  record,
  string,
  tuple,
  unknown,
} from "../lib/validation";
import { operatingCurrenciesWithConversion } from "../stores";

export interface AccountHierarchyDatum {
  account: string;
  balance: Partial<Record<string, number>>;
  dummy?: boolean;
}
type AccountHierarchy = TreeNode<AccountHierarchyDatum>;
export type AccountHierarchyNode = HierarchyNode<AccountHierarchyDatum>;

/**
 * Add internal nodes as fake leaf nodes to their own children.
 *
 * In the treemap, we only render leaf nodes, so for accounts that have both
 * children and a balance, we want to duplicate them as leaf nodes.
 */
function addInternalNodesAsLeaves(node: AccountHierarchy): void {
  if (node.children.length) {
    node.children.forEach(addInternalNodesAsLeaves);
    node.children.push({ ...node, children: [], dummy: true });
    node.balance = {};
  }
}

export interface ScatterPlotDatum {
  date: Date;
  type: string;
  description: string;
}

export interface LineChartDatum {
  name: string;
  date: Date;
  value: number;
}

export type LineChartData = {
  name: string;
  values: LineChartDatum[];
};

export interface BarChartDatumValue {
  name: string;
  value: number;
  budget: number;
}

export interface BarChartDatum {
  label: string;
  date: Date;
  values: BarChartDatumValue[];
}

export interface HierarchyChart {
  type: "hierarchy";
  data: Map<string, AccountHierarchyNode>;
  tooltipText?: undefined;
}

export interface BarChart {
  type: "barchart";
  data: BarChartDatum[];
  tooltipText: (c: FormatterContext, d: BarChartDatum) => string;
}

export interface LineChart {
  type: "linechart";
  data: LineChartData[];
  tooltipText: (c: FormatterContext, d: LineChartDatum) => string;
}

export interface ScatterPlot {
  type: "scatterplot";
  data: ScatterPlotDatum[];
  tooltipText?: undefined;
}

export type ChartTypes = HierarchyChart | BarChart | ScatterPlot | LineChart;

const balances_validator = array(object({ date, balance: record(number) }));

export function balances(json: unknown): Result<LineChart, string> {
  const res = balances_validator(json);
  if (!res.success) {
    return res;
  }
  const parsedData = res.value;
  const groups = new Map<string, LineChartDatum[]>();
  for (const { date: date_, balance } of parsedData) {
    Object.entries(balance).forEach(([currency, value]) => {
      const group = groups.get(currency);
      const datum = { date: date_, value, name: currency };
      if (group) {
        group.push(datum);
      } else {
        groups.set(currency, [datum]);
      }
    });
  }
  const data = [...groups.entries()].map(([name, values]) => ({
    name,
    values,
  }));

  return ok({
    type: "linechart" as const,
    data,
    tooltipText: (c, d) =>
      `${c.currency(d.value)} ${d.name}<em>${dateFormat.day(d.date)}</em>`,
  });
}

const commodities_validator = object({
  quote: string,
  base: string,
  prices: array(tuple([date, number])),
});

export function commodities(
  json: unknown,
  label: string
): Result<LineChart, string> {
  const res = commodities_validator(json);
  if (!res.success) {
    return res;
  }
  const { base, quote, prices } = res.value;
  const values = prices.map((d) => ({ name: label, date: d[0], value: d[1] }));
  return ok({
    type: "linechart" as const,
    data: [{ name: label, values }],
    tooltipText(c, d) {
      return `1 ${base} = ${c.currency(d.value)} ${quote}<em>${dateFormat.day(
        d.date
      )}</em>`;
    },
  });
}

const bar_validator = array(
  object({ date, budgets: record(number), balance: record(number) })
);

export function bar(json: unknown): Result<BarChart, string> {
  const res = bar_validator(json);
  if (!res.success) {
    return res;
  }
  const parsedData = res.value;
  const currentDateFmt = get(currentDateFormat);
  const data = parsedData.map((d) => ({
    values: get(operatingCurrenciesWithConversion).map((name: string) => ({
      name,
      value: d.balance[name] || 0,
      budget: d.budgets[name] || 0,
    })),
    date: d.date,
    label: currentDateFmt(d.date),
  }));
  return ok({
    type: "barchart" as const,
    data,
    tooltipText: (c, d) => {
      let text = "";
      d.values.forEach((a) => {
        text += `${c.currency(a.value)} ${a.name}`;
        if (a.budget) {
          text += ` / ${c.currency(a.budget)} ${a.name}`;
        }
        text += "<br>";
      });
      text += `<em>${d.label}</em>`;
      return text;
    },
  });
}

const scatterplot_validator = array(
  object({ type: string, date, description: string })
);

export function scatterplot(json: unknown): Result<ScatterPlot, string> {
  const res = scatterplot_validator(json);
  if (!res.success) {
    return res;
  }
  return ok({ type: "scatterplot" as const, data: res.value });
}

const account_hierarchy_validator: Validator<AccountHierarchy> = object({
  account: string,
  balance: record(number),
  children: lazy(() => array(account_hierarchy_validator)),
});
const hierarchy_validator = object({
  root: account_hierarchy_validator,
  modifier: number,
});

export function hierarchy(json: unknown): Result<HierarchyChart, string> {
  const res = hierarchy_validator(json);
  if (!res.success) {
    return res;
  }
  const { root, modifier } = res.value;
  addInternalNodesAsLeaves(root);
  const data = new Map<string, AccountHierarchyNode>();

  get(operatingCurrenciesWithConversion).forEach((currency: string) => {
    const currencyHierarchy = d3Hierarchy(root)
      .sum((d) => (d.balance[currency] || 0) * modifier)
      .sort((a, b) => (b.value || 0) - (a.value || 0));
    if (currencyHierarchy.value) {
      data.set(currency, currencyHierarchy);
    }
  });

  return ok({ type: "hierarchy" as const, data });
}

const parsers: Partial<
  Record<string, (json: unknown, label: string) => Result<ChartTypes, string>>
> = {
  balances,
  commodities,
  bar,
  hierarchy,
  scatterplot,
};

export type NamedChartTypes = ChartTypes & {
  name?: string;
};

const chart_data_validator = array(
  object({ label: string, type: string, data: unknown })
);

export function parseChartData(): Result<NamedChartTypes[], string> {
  const json_res = getScriptTagJSON("#chart-data");
  if (!json_res.success) {
    return json_res;
  }
  const res = chart_data_validator(json_res.value);
  if (!res.success) {
    return res;
  }
  const chartData = res.value;
  const result: NamedChartTypes[] = [];
  chartData.forEach((chart) => {
    const parser = parsers[chart.type];
    if (parser) {
      const r = parser(chart.data, chart.label);
      if (r.success) {
        result.push({ name: chart.label, ...r.value });
      }
    }
  });
  return ok(result);
}

const grouped_chart_validator = array(
  object({ group: string, balance: record(number) })
);
export function parseGroupedQueryChart(
  json: unknown,
  currencies: string[]
): Result<HierarchyChart, string> {
  const grouped = grouped_chart_validator(json);
  if (!grouped.success) {
    return err("No grouped query data");
  }
  if (!grouped.value[0].group) {
    throw new Error("asdf");
  }
  const root = stratify(
    grouped.value,
    (d) => d.group,
    (account, d) => ({ account, balance: d?.balance ?? {} })
  );
  root.account = "(root)";

  const data = new Map<string, AccountHierarchyNode>();
  currencies.forEach((currency: string) => {
    const currencyHierarchy: AccountHierarchyNode = d3Hierarchy(root)
      .sum((d) => d.balance[currency] || 0)
      .sort((a, b) => (b.value || 0) - (a.value || 0));
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
  operating_currencies: string[]
): Result<ChartTypes, string> {
  const tree = parseGroupedQueryChart(json, operating_currencies);
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
