import type { Result } from "../lib/result.ts";
import type { ValidationError } from "../lib/validation.ts";
import { array, date, object, string } from "../lib/validation.ts";

/** Data point for the scatterplot (events). */
export interface ScatterPlotDatum {
  readonly date: Date;
  readonly type: string;
  readonly description: string;
}

export class ScatterPlot {
  readonly type = "scatterplot";
  readonly name: string | null;
  readonly data: readonly ScatterPlotDatum[];

  constructor(name: string | null, data: readonly ScatterPlotDatum[]) {
    this.name = name;
    this.data = data;
  }
}

const scatterplot_validator = array<ScatterPlotDatum>(
  object({ type: string, date, description: string }),
);

export function scatterplot(
  label: string | null,
  json: unknown,
): Result<ScatterPlot, ValidationError> {
  return scatterplot_validator(json).map(
    (value) => new ScatterPlot(label, value),
  );
}
