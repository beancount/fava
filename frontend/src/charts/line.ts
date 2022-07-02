import type { FormatterContext } from "../format";
import { day } from "../format";
import { ok } from "../lib/result";
import type { Result } from "../lib/result";
import {
  array,
  date,
  number,
  object,
  record,
  string,
  tuple,
} from "../lib/validation";

export interface LineChartDatum {
  name: string;
  date: Date;
  value: number;
}

export type LineChartData = {
  name: string;
  values: LineChartDatum[];
};

export interface LineChart {
  type: "linechart";
  data: LineChartData[];
  tooltipText: (c: FormatterContext, d: LineChartDatum) => string;
}

const balances_validator = array(object({ date, balance: record(number) }));

export function balances(json: unknown): Result<LineChart, string> {
  const res = balances_validator(json);
  if (!res.success) {
    return res;
  }
  const parsedData = res.value;
  const groups = new Map<string, LineChartDatum[]>();
  for (const { date: date_, balance } of parsedData) {
    Object.entries(balance).forEach(([currency, value]) => {
      const group = groups.get(currency);
      const datum = { date: date_, value, name: currency };
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

  return ok({
    type: "linechart" as const,
    data,
    tooltipText: (c, d) =>
      `${c.amount(d.value, d.name)}<em>${day(d.date)}</em>`,
  });
}

const commodities_validator = object({
  quote: string,
  base: string,
  prices: array(tuple([date, number])),
});

export function commodities(
  json: unknown,
  _ctx: unknown,
  label: string
): Result<LineChart, string> {
  const res = commodities_validator(json);
  if (!res.success) {
    return res;
  }
  const { base, quote, prices } = res.value;
  const values = prices.map((d) => ({ name: label, date: d[0], value: d[1] }));
  return ok({
    type: "linechart" as const,
    data: [{ name: label, values }],
    tooltipText(c, d) {
      return `1 ${base} = ${c.amount(d.value, quote)}<em>${day(d.date)}</em>`;
    },
  });
}
