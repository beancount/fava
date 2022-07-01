import type { FormatterContext } from "../format";
import { ok } from "../lib/result";
import type { Result } from "../lib/result";
import { array, date, number, object, record } from "../lib/validation";

import type { ChartContext } from "./context";

export interface BarChartDatumValue {
  name: string;
  value: number;
  children: Map<string, number>;
  budget: number;
}

export interface BarChartDatum {
  label: string;
  date: Date;
  values: BarChartDatumValue[];
}

export interface BarChart {
  type: "barchart";
  data: { series: BarChartDatum[]; hasStackedData: boolean };
  tooltipText: (c: FormatterContext, d: BarChartDatum, e: string) => string;
}

const bar_validator = array(
  object({
    date,
    budgets: record(number),
    balance: record(number),
    account_balances: record(record(number)),
  })
);

/**
 * Try to parse a bar chart.
 */
export function bar(
  json: unknown,
  { currencies, dateFormat }: ChartContext
): Result<BarChart, string> {
  const res = bar_validator(json);
  if (!res.success) {
    return res;
  }
  const parsedData = res.value;
  const series = parsedData.map((interval) => ({
    values: currencies.map((currency) => ({
      name: currency,
      value: interval.balance[currency] ?? 0,
      children: new Map<string, number>(
        Object.keys(interval.account_balances).map((name) => [
          name,
          interval.account_balances[name][currency] ?? 0,
        ])
      ),
      budget: interval.budgets[currency] ?? 0,
    })),
    date: interval.date,
    label: dateFormat(interval.date),
  }));
  const hasStackedData = series.some((interval) =>
    interval.values.some((d) => d.children.size > 1)
  );

  return ok({
    type: "barchart" as const,
    data: { series, hasStackedData },
    tooltipText: (c, d, e) => {
      let text = "";
      if (e === "") {
        d.values.forEach((a) => {
          text += `${c.currency(a.value)} ${a.name}`;
          if (a.budget) {
            text += ` / ${c.currency(a.budget)} ${a.name}`;
          }
          text += "<br>";
        });
      } else {
        text += `<em>${e}</em>`;
        d.values.forEach((a) => {
          text += `${c.currency(a.children.get(e) ?? 0)} ${a.name}<br>`;
        });
      }
      text += `<em>${d.label}</em>`;
      return text;
    },
  });
}
