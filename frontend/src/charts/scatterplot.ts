import { ok } from "../lib/result";
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
  object({ type: string, date, description: string })
);

export function scatterplot(json: unknown): Result<ScatterPlot, string> {
  const res = scatterplot_validator(json);
  if (!res.success) {
    return res;
  }
  return ok({ type: "scatterplot" as const, data: res.value });
}
