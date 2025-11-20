/**
 * This module contains the main code to render Fava's charts.
 *
 * The charts heavily use d3 libraries.
 */

import type { Validator } from "../lib/validation.ts";
import { array, tagged_union } from "../lib/validation.ts";
import type { BarChart } from "./bar.ts";
import { ParsedBarChart } from "./bar.ts";
import type { ChartContext } from "./context.ts";
import { type HierarchyChart, ParsedHierarchyChart } from "./hierarchy.ts";
import type { LineChart } from "./line.ts";
import { ParsedLineChart } from "./line.ts";
import { ScatterPlot } from "./scatterplot.ts";

export type FavaChart = HierarchyChart | BarChart | ScatterPlot | LineChart;

/*
 * The charts are parsed / loaded from the raw JSON into classed implementing
 * this interface and can be provided the context before rendering.
 */
export interface ParsedFavaChart {
  readonly label: string | null;
  with_context($chartContext: ChartContext): FavaChart;
}

export const chart_validator: Validator<ParsedFavaChart[]> = array(
  tagged_union("type", {
    balances: ParsedLineChart.validator,
    bar: ParsedBarChart.validator,
    hierarchy: ParsedHierarchyChart.validator,
    scatterplot: ScatterPlot.validator,
  }),
);
