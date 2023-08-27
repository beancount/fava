/**
 * This module contains the main code to render Fava's charts.
 *
 * The charts heavily use d3 libraries.
 */

import type { Result } from "../lib/result";
import { array, object, string, unknown } from "../lib/validation";

import { bar } from "./bar";
import type { BarChart } from "./bar";
import type { ChartContext } from "./context";
import { hierarchy } from "./hierarchy";
import type { HierarchyChart } from "./hierarchy";
import { balances } from "./line";
import type { LineChart } from "./line";
import { scatterplot } from "./scatterplot";
import type { ScatterPlot } from "./scatterplot";

const parsers: Record<
  string,
  (
    label: string,
    json: unknown,
    $chartContext: ChartContext,
  ) => Result<FavaChart, string>
> = {
  balances,
  bar,
  hierarchy,
  scatterplot,
};

export type FavaChart = HierarchyChart | BarChart | ScatterPlot | LineChart;

const chart_data_validator = array(
  object({ label: string, type: string, data: unknown }),
);

export function parseChartData(
  data: unknown,
  $chartContext: ChartContext,
): Result<FavaChart[], string> {
  return chart_data_validator(data).map((chartData) => {
    const result: FavaChart[] = [];
    chartData.forEach((chart) => {
      const parser = parsers[chart.type];
      if (parser) {
        const r = parser(chart.label, chart.data, $chartContext);
        if (r.is_ok) {
          result.push(r.value);
        }
      }
    });
    return result;
  });
}
