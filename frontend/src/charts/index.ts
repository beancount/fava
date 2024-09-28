/**
 * This module contains the main code to render Fava's charts.
 *
 * The charts heavily use d3 libraries.
 */

import { collect, err, type Result } from "../lib/result";
import type { ValidationError } from "../lib/validation";
import { array, object, string, unknown } from "../lib/validation";
import type { BarChart } from "./bar";
import { bar } from "./bar";
import type { ChartContext } from "./context";
import type { HierarchyChart } from "./hierarchy";
import { hierarchy } from "./hierarchy";
import type { LineChart } from "./line";
import { balances } from "./line";
import type { ScatterPlot } from "./scatterplot";
import { scatterplot } from "./scatterplot";

const parsers: Record<
  string,
  (
    label: string,
    json: unknown,
    $chartContext: ChartContext,
  ) => Result<FavaChart, ValidationError>
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

class ChartValidationError extends Error {
  constructor(type: string, cause: ValidationError) {
    super(`Parsing of data for ${type} chart failed.`, { cause });
  }
}

class UnknownChartTypeError extends Error {
  constructor(type: string) {
    super(`Unknown chart type ${type}`);
  }
}

export function parseChartData(
  data: unknown,
  $chartContext: ChartContext,
): Result<FavaChart[], ChartValidationError | UnknownChartTypeError> {
  return chart_data_validator(data).and_then((chartData) =>
    collect(
      chartData.map(({ type, label, data }) => {
        const parser = parsers[type];
        return parser
          ? parser(label, data, $chartContext).map_err(
              (error) => new ChartValidationError(type, error),
            )
          : err(new UnknownChartTypeError(type));
      }),
    ),
  );
}
