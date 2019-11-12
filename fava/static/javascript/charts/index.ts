/**
 * This module contains the main code to render Fava's charts.
 *
 * The charts heavily use d3 libraries.
 */

import { hierarchy } from "d3-hierarchy";
import "d3-transition";

import { getScriptTagJSON } from "../helpers";
import { favaAPI, conversion } from "../stores";
import e from "../events";
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
} from "../validation";

import { BaseChart } from "./base";
import { BarChart } from "./bar";
import { LineChart } from "./line";
import { ScatterPlot } from "./scatter";
import {
  addInternalNodesAsLeaves,
  HierarchyContainer,
  AccountHierarchy,
  AccountHierarchyNode,
} from "./hierarchy";
import { scales } from "./helpers";

/**
 * The list of operating currencies, adding in the current conversion currency.
 */
let operatingCurrenciesWithConversion: string[] = [];
conversion.subscribe(conversionValue => {
  if (
    !conversionValue ||
    ["at_cost", "at_value", "units"].includes(conversionValue) ||
    favaAPI.options.operating_currency.includes(conversionValue)
  ) {
    operatingCurrenciesWithConversion = favaAPI.options.operating_currency;
  } else {
    operatingCurrenciesWithConversion = [
      ...favaAPI.options.operating_currency,
      conversionValue,
    ];
  }
});

e.on("page-init", () => {
  const { accounts, options } = favaAPI;
  scales.treemap.domain(accounts);
  scales.sunburst.domain(accounts);
  options.operating_currency.sort();
  options.commodities.sort();
  scales.currencies.domain([
    ...options.operating_currency,
    ...options.commodities,
  ]);
});

type FirstParameter<T> = T extends (arg: infer P) => any ? P : never;

interface ChartWithData<T extends BaseChart> {
  data: FirstParameter<T["draw"]>;
  renderer: (svg: SVGElement) => T;
}

const parsers: Partial<Record<
  string,
  (json: unknown, label: string) => ChartWithData<any>
>> = {
  balances(json: unknown): ChartWithData<LineChart> {
    const series: Record<
      string,
      { name: string; values: { date: Date; name: string; value: number }[] }
    > = {};
    const parsedData = array(
      object({
        date,
        balance: record(number),
      })
    )(json);
    parsedData.forEach(({ date: date_, balance }) => {
      Object.entries(balance).forEach(([currency, value]) => {
        const currencySeries = series[currency] || {
          name: currency,
          values: [],
        };
        currencySeries.values.push({
          name: currency,
          date: date_,
          value,
        });
        series[currency] = currencySeries;
      });
    });

    return {
      data: Object.values(series),
      renderer: (svg: SVGElement) =>
        new LineChart(svg).set(
          "tooltipText",
          d =>
            `${formatCurrency(d.value)} ${d.name}<em>${dateFormat.day(
              d.date
            )}</em>`
        ),
    };
  },
  commodities(json: unknown, label: string): ChartWithData<LineChart> {
    const parsedData = object({
      quote: string,
      base: string,
      prices: array(tuple([date, number])),
    })(json);

    const renderer = (svg: SVGElement) =>
      new LineChart(svg).set(
        "tooltipText",
        d =>
          `1 ${parsedData.base} = ${formatCurrency(d.value)} ${
            parsedData.quote
          }<em>${dateFormat.day(d.date)}</em>`
      );
    return {
      data: [
        {
          name: label,
          values: parsedData.prices.map(d => ({
            name: label,
            date: d[0],
            value: d[1],
          })),
        },
      ],
      renderer,
    };
  },
  bar(json: unknown): ChartWithData<BarChart> {
    const jsonData = array(
      object({ date, budgets: record(number), balance: record(number) })
    )(json);
    const data = jsonData.map(d => ({
      values: operatingCurrenciesWithConversion.map(name => ({
        name,
        value: d.balance[name] || 0,
        budget: d.budgets[name] || 0,
      })),
      date: d.date,
      label: currentDateFormat(d.date),
    }));
    const renderer = (svg: SVGElement) =>
      new BarChart(svg).set("tooltipText", d => {
        let text = "";
        d.values.forEach(a => {
          text += `${formatCurrency(a.value)} ${a.name}`;
          if (a.budget) {
            text += ` / ${formatCurrency(a.budget)} ${a.name}`;
          }
          text += "<br>";
        });
        text += `<em>${d.label}</em>`;
        return text;
      });
    return { data, renderer };
  },
  hierarchy(json: unknown): ChartWithData<HierarchyContainer> {
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

    operatingCurrenciesWithConversion.forEach(currency => {
      const currencyHierarchy: AccountHierarchyNode = hierarchy(root)
        .sum(d => d.balance[currency] * modifier)
        .sort((a, b) => (b.value || 0) - (a.value || 0));
      if (currencyHierarchy.value !== 0) {
        data[currency] = currencyHierarchy;
      }
    });

    return {
      data,
      renderer: (svg: SVGElement) => new HierarchyContainer(svg),
    };
  },
  scatterplot(json: unknown): ChartWithData<ScatterPlot> {
    const parser = array(
      object({
        type: string,
        date,
        description: string,
      })
    );
    return {
      data: parser(json),
      renderer: (svg: SVGElement) => new ScatterPlot(svg),
    };
  },
};

const validateChartData = array(
  object({
    label: string,
    type: string,
    data: unknown,
  })
);
export function parseChartData() {
  const chartData = validateChartData(getScriptTagJSON("#chart-data"));
  const result: (ChartWithData<any> & { name: string })[] = [];
  chartData.forEach(chart => {
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
