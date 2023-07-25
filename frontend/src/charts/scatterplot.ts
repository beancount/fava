import type { Result } from "../lib/result";
import { array, date, object, string } from "../lib/validation";

export interface ScatterPlotDatum {
  date: Date;
  type: string;
  description: string;
}

export interface ScatterPlot {
  type: "scatterplot";
  data: ScatterPlotDatum[];
}

const scatterplot_validator = array(
  object({ type: string, date, description: string }),
);

export function scatterplot(json: unknown): Result<ScatterPlot, string> {
  return scatterplot_validator(json).map((value) => ({
    type: "scatterplot",
    data: value,
  }));
}
