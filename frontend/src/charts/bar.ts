import type { Series } from "d3-shape";
import { stack, stackOffsetDiverging } from "d3-shape";

import type { FormatterContext } from "../format";
import { ok } from "../lib/result";
import type { Result } from "../lib/result";
import { array, date, number, object, record } from "../lib/validation";

import type { ChartContext } from "./context";
import type { TooltipContent } from "./tooltip";
import { domHelpers } from "./tooltip";

export interface BarChartDatumValue {
  currency: string;
  value: number;
  budget: number;
}

/** The data for the bars of one interval. */
export interface BarChartDatum {
  /** The label of this interval. */
  label: string;
  /** The date of this interval. */
  date: Date;
  /** One value for each (operating) currency. */
  values: BarChartDatumValue[];
  /** The balances of the child accounts. */
  account_balances: Record<string, Record<string, number>>;
}

export interface BarChart {
  type: "barchart";
  data: {
    /** All accounts that occur as some child account. */
    accounts: string[];
    /** The data for the (single) bars for all the intervals in this chart. */
    bar_groups: BarChartDatum[];
    /** For each currency, the stacks (one series per account) */
    stacks: [currency: string, stacks: Series<BarChartDatum, string>[]][];
    /** Whether this chart contains any stacks (or is just a single account). */
    hasStackedData: boolean;
  };
  tooltipText: (
    c: FormatterContext,
    d: BarChartDatum,
    e: string
  ) => TooltipContent;
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
  const bar_groups = parsedData.map((interval) => ({
    values: currencies.map((currency) => ({
      currency,
      value: interval.balance[currency] ?? 0,
      budget: interval.budgets[currency] ?? 0,
    })),
    date: interval.date,
    label: dateFormat(interval.date),
    account_balances: interval.account_balances,
  }));
  const accounts = Array.from(
    new Set(parsedData.map((d) => [...Object.keys(d.account_balances)]).flat(2))
  ).sort();
  const hasStackedData = accounts.length > 1;

  const stacks = currencies.map(
    (currency): [string, Series<BarChartDatum, string>[]] => [
      currency,
      stack<BarChartDatum>()
        .keys(accounts)
        .value((obj, key) => obj.account_balances[key]?.[currency] ?? 0)
        .offset(stackOffsetDiverging)(bar_groups),
    ]
  );

  return ok({
    type: "barchart" as const,
    data: { accounts, bar_groups, stacks, hasStackedData },
    tooltipText: (c, d, e) => {
      const content: TooltipContent = [];
      if (e === "") {
        d.values.forEach((a) => {
          content.push(
            domHelpers.t(
              a.budget
                ? `${c.amount(a.value, a.currency)} / ${c.amount(
                    a.budget,
                    a.currency
                  )}`
                : c.amount(a.value, a.currency)
            )
          );
          content.push(domHelpers.br());
        });
      } else {
        content.push(domHelpers.em(e));
        d.values.forEach((a) => {
          const value = d.account_balances[e]?.[a.currency] ?? 0;
          content.push(domHelpers.t(`${c.amount(value, a.currency)}`));
          content.push(domHelpers.br());
        });
      }
      content.push(domHelpers.em(d.label));
      return content;
    },
  });
}
