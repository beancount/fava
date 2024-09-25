import { sort } from "d3-array";

import type { FormatterContext } from "../format";
import { day } from "../format";
import type { Result } from "../lib/result";
import type { ValidationError } from "../lib/validation";
import { array, date, number, object, record } from "../lib/validation";
import type { TooltipContent } from "./tooltip";
import { domHelpers } from "./tooltip";

/**
 * A single data point on a line or area chart.
 */
export interface LineChartDatum {
  readonly name: string;
  readonly date: Date;
  readonly value: number;
}

/**
 * A series of values for a line chart, e.g., for a single currency.
 */
interface LineChartSeries {
  readonly name: string;
  readonly values: readonly LineChartDatum[];
}

/**
 * A line or area chart.
 *
 * This consists of several series of points, e.g., a line for each currency
 * in the balances of an account.
 */
export class LineChart {
  readonly type = "linechart";

  readonly series_names: readonly string[];

  constructor(
    readonly name: string | null,
    private readonly data: readonly LineChartSeries[],
    readonly tooltipText: (
      c: FormatterContext,
      d: LineChartDatum,
    ) => TooltipContent,
  ) {
    this.data = sort(data, (d) => -d.values.length);
    this.series_names = this.data.map((series) => series.name);
  }

  /** Filter the data of this chart, excluding some series. */
  filter(hidden_names: readonly string[]): LineChartSeries[] {
    const hidden_names_set = new Set(hidden_names);
    return this.data.filter((series) => !hidden_names_set.has(series.name));
  }
}

const balances_validator = array(object({ date, balance: record(number) }));

export function balances_from_parsed_data(
  label: string | null,
  parsed_data: { date: Date; balance: Record<string, number> }[],
): LineChart {
  const groups = new Map<string, LineChartDatum[]>();
  for (const { date: date_val, balance } of parsed_data) {
    Object.entries(balance).forEach(([currency, value]) => {
      const group = groups.get(currency);
      const datum = { date: date_val, value, name: currency };
      if (group) {
        group.push(datum);
      } else {
        groups.set(currency, [datum]);
      }
    });
  }
  const data = [...groups.entries()].map(([name, values]) => ({
    name,
    values,
  }));

  return new LineChart(label, data, (c, d) => [
    domHelpers.t(c.amount(d.value, d.name)),
    domHelpers.em(day(d.date)),
  ]);
}

export function balances(
  label: string | null,
  json: unknown,
): Result<LineChart, ValidationError> {
  return balances_validator(json).map((parsedData) =>
    balances_from_parsed_data(label, parsedData),
  );
}
