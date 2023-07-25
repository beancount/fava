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

const parsers: Partial<
  Record<
    string,
    (
      json: unknown,
      ctx: ChartContext,
      label: string,
    ) => Result<FavaChart, string>
  >
> = {
  balances,
  bar,
  hierarchy,
  scatterplot,
};

export type FavaChart = HierarchyChart | BarChart | ScatterPlot | LineChart;
export type NamedFavaChart = FavaChart & { name?: string };

const chart_data_validator = array(
  object({ label: string, type: string, data: unknown }),
);

export function parseChartData(
  data: unknown,
  ctx: ChartContext,
): Result<NamedFavaChart[], string> {
  return chart_data_validator(data).map((chartData) => {
    const result: NamedFavaChart[] = [];
    chartData.forEach((chart) => {
      const parser = parsers[chart.type];
      if (parser) {
        const r = parser(chart.data, ctx, chart.label);
        if (r.is_ok) {
          result.push({ name: chart.label, ...r.value });
        }
      }
    });
    return result;
  });
}
