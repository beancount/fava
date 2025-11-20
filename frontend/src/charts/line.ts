import { sort } from "d3-array";

import type { FormatterContext } from "../format.ts";
import { day } from "../format.ts";
import type { Validator } from "../lib/validation.ts";
import {
  array,
  date,
  number,
  object,
  record,
  string,
} from "../lib/validation.ts";
import type { ParsedFavaChart } from "./index.ts";
import type { TooltipContent } from "./tooltip.ts";
import { domHelpers } from "./tooltip.ts";

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
  readonly label: string | null;
  private readonly data: readonly LineChartSeries[];
  readonly tooltipText: (
    c: FormatterContext,
    d: LineChartDatum,
  ) => TooltipContent;

  constructor(
    label: string | null,
    data: readonly LineChartSeries[],
    tooltipText: (c: FormatterContext, d: LineChartDatum) => TooltipContent,
  ) {
    this.label = label;
    this.data = sort(data, (d) => -d.values.length);
    this.tooltipText = tooltipText;
    this.series_names = this.data.map((series) => series.name);
  }

  /** Filter the data of this chart, excluding some series. */
  filter(hidden_names: readonly string[]): LineChartSeries[] {
    const hidden_names_set = new Set(hidden_names);
    return this.data.filter((series) => !hidden_names_set.has(series.name));
  }

  with_context(): this {
    return this;
  }
}

const balances_validator = object({
  label: string,
  data: array(object({ date, balance: record(number) })),
});

type ParsedLineChartData = { date: Date; balance: Record<string, number> }[];

export class ParsedLineChart implements ParsedFavaChart {
  readonly label: string | null;
  readonly data: ParsedLineChartData;

  constructor(label: string | null, data: ParsedLineChartData) {
    this.label = label;
    this.data = data;
  }

  static validator: Validator<ParsedLineChart> = (json) =>
    balances_validator(json).map(
      ({ label, data }) => new ParsedLineChart(label, data),
    );

  with_context(): LineChart {
    const groups = new Map<string, LineChartDatum[]>();
    for (const { date: date_val, balance } of this.data) {
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

    return new LineChart(this.label, data, (c, d) => [
      domHelpers.t(c.amount(d.value, d.name)),
      domHelpers.em(day(d.date)),
    ]);
  }
}
