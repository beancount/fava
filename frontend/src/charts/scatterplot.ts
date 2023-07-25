import type { Result } from "../lib/result";
import { array, date, object, string } from "../lib/validation";

export interface ScatterPlotDatum {
  date: Date;
  type: string;
  description: string;
}

export class ScatterPlot {
  readonly type = "scatterplot";

  constructor(
    readonly name: string | null,
    readonly data: ScatterPlotDatum[],
  ) {}
}

const scatterplot_validator = array(
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
