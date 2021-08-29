import type { FormatterContext } from "../format";
import { ok } from "../lib/result";
import type { Result } from "../lib/result";
import { array, date, number, object, record } from "../lib/validation";

import type { ChartContext } from "./context";

export interface BarChartDatumValue {
  name: string;
  value: number;
  budget: number;
}

export interface BarChartDatum {
  label: string;
  date: Date;
  values: BarChartDatumValue[];
}

export interface BarChart {
  type: "barchart";
  data: BarChartDatum[];
  tooltipText: (c: FormatterContext, d: BarChartDatum) => string;
}

const bar_validator = array(
  object({ date, budgets: record(number), balance: record(number) })
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
  const data = parsedData.map((d) => ({
    values: currencies.map((name) => ({
      name,
      value: d.balance[name] ?? 0,
      budget: d.budgets[name] ?? 0,
    })),
    date: d.date,
    label: dateFormat(d.date),
  }));
  return ok({
    type: "barchart" as const,
    data,
    tooltipText: (c, d) => {
      let text = "";
      d.values.forEach((a) => {
        text += `${c.currency(a.value)} ${a.name}`;
        if (a.budget) {
          text += ` / ${c.currency(a.budget)} ${a.name}`;
        }
        text += "<br>";
      });
      text += `<em>${d.label}</em>`;
      return text;
    },
  });
}
