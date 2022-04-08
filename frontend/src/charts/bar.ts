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
  data: BarChartDatum[];
  hasStackedData: boolean;
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
  const data = parsedData.map((d) => ({
    values: currencies.map((name) => ({
      name,
      value: d.balance[name] ?? 0,
      children: new Map<string, number>(
        Object.entries(
          Object.keys(d.account_balances).reduce(
            (o, key) => ({ ...o, [key]: d.account_balances[key][name] ?? 0 }),
            {}
          )
        )
      ),
      budget: d.budgets[name] ?? 0,
    })),
    date: d.date,
    label: dateFormat(d.date),
  }));
  return ok({
    type: "barchart" as const,
    data,
    hasStackedData:
      data.reduce(
        (prev1, cur1) =>
          prev1 +
          cur1.values.reduce((prev2, cur2) => prev2 + cur2.children.size, 0),
        0
      ) > 1,
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
        text += `<em>${e.replace(/^:/, "")}</em>`;
        d.values.forEach((a) => {
          text += `${c.currency(a.children.get(e) ?? 0)} ${a.name}<br>`;
        });
      }
      text += `<em>${d.label}</em>`;
      return text;
    },
  });
}
