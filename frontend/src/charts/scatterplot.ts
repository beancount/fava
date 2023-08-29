import type { Result } from "../lib/result";
import { array, date, object, string } from "../lib/validation";

/** Data point for the scatterplot (events). */
export interface ScatterPlotDatum {
  readonly date: Date;
  readonly type: string;
  readonly description: string;
}

export class ScatterPlot {
  readonly type = "scatterplot";

  constructor(
    readonly name: string | null,
    readonly data: readonly ScatterPlotDatum[],
  ) {}
}

const scatterplot_validator = array<ScatterPlotDatum>(
  object({ type: string, date, description: string }),
);

export function scatterplot(
  label: string | null,
  json: unknown,
): Result<ScatterPlot, string> {
  return scatterplot_validator(json).map(
    (value) => new ScatterPlot(label, value),
  );
}
