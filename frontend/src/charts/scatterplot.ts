import type { Validator } from "../lib/validation.ts";
import { array, date, object, string } from "../lib/validation.ts";
import type { ParsedFavaChart } from "./index.ts";

/** Data point for the scatterplot (events). */
export interface ScatterPlotDatum {
  readonly date: Date;
  readonly type: string;
  readonly description: string;
}

const scatterplot_validator = object({
  label: string,
  data: array<ScatterPlotDatum>(
    object({ type: string, date, description: string }),
  ),
});

export class ScatterPlot implements ParsedFavaChart {
  readonly type = "scatterplot";
  readonly label: string | null;
  readonly data: readonly ScatterPlotDatum[];

  constructor(label: string | null, data: readonly ScatterPlotDatum[]) {
    this.label = label;
    this.data = data;
  }

  static validator: Validator<ScatterPlot> = (json) =>
    scatterplot_validator(json).map(
      ({ label, data }) => new ScatterPlot(label, data),
    );

  with_context(): this {
    return this;
  }
}
