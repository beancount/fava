/**
 * This module contains the main code to render Fava's charts.
 *
 * The charts heavily use d3 libraries.
 */

import { hierarchy, HierarchyNode } from "d3-hierarchy";
import { derived, get } from "svelte/store";

import { getScriptTagJSON } from "../lib/dom";
import { conversion, operating_currency } from "../stores";
import { formatCurrency, dateFormat, currentDateFormat } from "../format";
import {
  array,
  date,
  object,
  record,
  number,
  string,
  tuple,
  unknown,
  lazy,
  Validator,
} from "../lib/validation";

export interface AccountHierarchyDatum {
  account: string;
  balance: Record<string, number | undefined>;
  dummy?: boolean;
}
interface AccountHierarchy extends AccountHierarchyDatum {
  children: AccountHierarchy[];
}
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

interface BarChartDatumValue {
  name: string;
  value: number;
  budget: number;
}

export interface BarChartDatum {
  label: string;
  date: Date;
  values: BarChartDatumValue[];
}

/**
 * The list of operating currencies, adding in the current conversion currency.
 */
const operatingCurrenciesWithConversion = derived(
  [operating_currency, conversion],
  ([operating_currency_val, conversion_val]) => {
    if (
      !conversion_val ||
      ["at_cost", "at_value", "units"].includes(conversion_val) ||
      operating_currency_val.includes(conversion_val)
    ) {
      return operating_currency_val;
    }
    return [...operating_currency_val, conversion_val];
  }
);

export interface HierarchyChart {
  type: "hierarchy";
  data: Record<string, AccountHierarchyNode>;
  tooltipText?: undefined;
}

interface BarChart {
  type: "barchart";
  data: BarChartDatum[];
  tooltipText(d: BarChartDatum): string;
}

interface LineChart {
  type: "linechart";
  data: LineChartData[];
  tooltipText(d: LineChartDatum): string;
}

interface ScatterPlot {
  type: "scatterplot";
  data: ScatterPlotDatum[];
  tooltipText?: undefined;
}

type ChartTypes = HierarchyChart | BarChart | ScatterPlot | LineChart;

const parsers: Record<string, (json: unknown, label: string) => ChartTypes> = {
  balances(json: unknown): LineChart {
    const parsedData = array(
      object({
        date,
        balance: record(number),
      })
    )(json);
    const groups: Map<string, LineChartDatum[]> = new Map();
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

    return {
      data,
      type: "linechart",
      tooltipText(d: LineChartDatum): string {
        return `${formatCurrency(d.value)} ${d.name}<em>${dateFormat.day(
          d.date
        )}</em>`;
      },
    };
  },
  commodities(json: unknown, label: string): LineChart {
    const parsedData = object({
      quote: string,
      base: string,
      prices: array(tuple([date, number])),
    })(json);
    return {
      data: [
        {
          name: label,
          values: parsedData.prices.map((d) => ({
            name: label,
            date: d[0],
            value: d[1],
          })),
        },
      ],
      type: "linechart",
      tooltipText(d: LineChartDatum): string {
        return `1 ${parsedData.base} = ${formatCurrency(d.value)} ${
          parsedData.quote
        }<em>${dateFormat.day(d.date)}</em>`;
      },
    };
  },
  bar(json: unknown): BarChart {
    const jsonData = array(
      object({ date, budgets: record(number), balance: record(number) })
    )(json);
    const currentDateFmt = get(currentDateFormat);
    const data = jsonData.map((d) => ({
      values: get(operatingCurrenciesWithConversion).map((name: string) => ({
        name,
        value: d.balance[name] || 0,
        budget: d.budgets[name] || 0,
      })),
      date: d.date,
      label: currentDateFmt(d.date),
    }));
    function tooltipText(d: BarChartDatum): string {
      let text = "";
      d.values.forEach((a) => {
        text += `${formatCurrency(a.value)} ${a.name}`;
        if (a.budget) {
          text += ` / ${formatCurrency(a.budget)} ${a.name}`;
        }
        text += "<br>";
      });
      text += `<em>${d.label}</em>`;
      return text;
    }
    return { data, tooltipText, type: "barchart" };
  },
  hierarchy(json: unknown): HierarchyChart {
    const hierarchyValidator: Validator<AccountHierarchy> = object({
      account: string,
      balance: record(number),
      balance_children: record(number),
      children: lazy(() => array(hierarchyValidator)),
    });
    const validator = object({
      root: hierarchyValidator,
      modifier: number,
    });
    const { root, modifier } = validator(json);
    addInternalNodesAsLeaves(root);
    const data: Record<string, AccountHierarchyNode> = {};

    get(operatingCurrenciesWithConversion).forEach((currency: string) => {
      const currencyHierarchy: AccountHierarchyNode = hierarchy(root)
        .sum((d) => (d.balance[currency] || 0) * modifier)
        .sort((a, b) => (b.value || 0) - (a.value || 0));
      if (currencyHierarchy.value) {
        data[currency] = currencyHierarchy;
      }
    });

    return {
      type: "hierarchy",
      data,
    };
  },
  scatterplot(json: unknown): ScatterPlot {
    return {
      type: "scatterplot",
      data: array(
        object({
          type: string,
          date,
          description: string,
        })
      )(json),
    };
  },
};

export type NamedChartTypes = ChartTypes & {
  name?: string;
};

export function parseChartData(): NamedChartTypes[] {
  const chartData = array(
    object({
      label: string,
      type: string,
      data: unknown,
    })
  )(getScriptTagJSON("#chart-data"));
  const result: NamedChartTypes[] = [];
  chartData.forEach((chart) => {
    const parser = parsers[chart.type];
    if (parser) {
      result.push({
        name: chart.label,
        ...parser(chart.data, chart.label),
      });
    }
  });
  return result;
}

export function parseQueryChart(data: unknown): ChartTypes | undefined {
  if (!Array.isArray(data) || !data.length) {
    return undefined;
  }
  if (data[0].group !== undefined) {
    const validated = array(object({ group: string, balance: record(number) }))(
      data
    );
    const root: AccountHierarchy = {
      account: "(root)",
      balance: {},
      children: [],
    };
    const accountMap: Map<string, AccountHierarchy> = new Map([
      [root.account, root],
    ]);
    const addNode = (node: AccountHierarchy): void => {
      const name = node.account;
      const existing = accountMap.get(name);
      if (existing) {
        existing.balance = node.balance;
        return;
      }
      accountMap.set(name, node);
      const parentEnd = name.lastIndexOf(":");
      const parentId = parentEnd > 0 ? name.slice(0, parentEnd) : root.account;
      let parent = accountMap.get(parentId);
      if (!parent) {
        parent = { account: parentId, balance: {}, children: [] };
        addNode(parent);
      }
      parent.children.push(node);
    };
    for (const { group: account = "(empty)", balance } of validated) {
      addNode({ account, balance, children: [] });
    }

    const chartData: Record<string, AccountHierarchyNode> = {};
    get(operatingCurrenciesWithConversion).forEach((currency: string) => {
      const currencyHierarchy: AccountHierarchyNode = hierarchy(root)
        .sum((d) => d.balance[currency] || 0)
        .sort((a, b) => (b.value || 0) - (a.value || 0));
      if (currencyHierarchy.value !== undefined) {
        chartData[currency] = currencyHierarchy;
      }
    });

    return {
      type: "hierarchy",
      data: chartData,
    };
  }
  if (data[0].date !== undefined) {
    return parsers.balances(data, "");
  }
  return undefined;
}
