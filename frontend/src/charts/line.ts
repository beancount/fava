import type { FormatterContext } from "../format";
import { day } from "../format";
import { ok } from "../lib/result";
import type { Result } from "../lib/result";
import { array, date, number, object, record } from "../lib/validation";

import type { TooltipContent } from "./tooltip";
import { domHelpers } from "./tooltip";

export interface LineChartDatum {
  name: string;
  date: Date;
  value: number;
}

export interface LineChartData {
  name: string;
  values: LineChartDatum[];
}

export interface LineChart {
  type: "linechart";
  data: LineChartData[];
  tooltipText: (c: FormatterContext, d: LineChartDatum) => TooltipContent;
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
    tooltipText: (c, d) => [
      domHelpers.t(c.amount(d.value, d.name)),
      domHelpers.em(day(d.date)),
    ],
  });
}
