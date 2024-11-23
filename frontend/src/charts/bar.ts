import { rollup } from "d3-array";
import type { Series } from "d3-shape";
import { stack, stackOffsetDiverging } from "d3-shape";

import type { FormatterContext } from "../format";
import type { Result } from "../lib/result";
import type { ValidationError, ValidationT } from "../lib/validation";
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

const bar_validator = array(
  object({
    date,
    budgets: record(number),
    balance: record(number),
    account_balances: record(record(number)),
  }),
);

type ParsedBarChartData = ValidationT<typeof bar_validator>;

export class BarChart {
  readonly type = "barchart";

  /** The accounts that occur in some bar.  */
  readonly accounts: string[];

  /** For each currency, the stacks (one series per account) */
  private readonly stacks: [
    currency: string,
    stacks: Series<BarChartDatum, string>[],
  ][];

  constructor(
    readonly name: string | null,
    /** The currencies that are shown in this bar chart. */
    readonly currencies: readonly string[],
    /** The data for the (single) bars for all the intervals in this chart. */
    private readonly bar_groups: BarChartDatum[],
  ) {
    this.accounts = Array.from(
      new Set(bar_groups.map((d) => Object.keys(d.account_balances)).flat(2)),
    ).sort();

    this.stacks = currencies.map((currency) => [
      currency,
      stack<BarChartDatum, string>()
        .keys(this.accounts)
        .value((d, account) => d.account_balances[account]?.[currency] ?? 0)
        .offset(stackOffsetDiverging)(bar_groups)
        .filter((b) => b[0] !== b[1] && !Number.isNaN(b[1])),
    ]);
  }

  filter(hidden_names: string[]): {
    currencies: string[];
    bar_groups: BarChartDatum[];
    stacks: [currency: string, stacks: Series<BarChartDatum, string>[]][];
  } {
    const hidden_names_set = new Set(hidden_names);
    const currencies = new Set(
      this.currencies.filter((c) => !hidden_names_set.has(c)),
    );
    const bar_groups = this.bar_groups.map((b) => ({
      ...b,
      values: b.values.filter((v) => currencies.has(v.currency)),
    }));
    const stacks = this.stacks.filter((s) => currencies.has(s[0]));
    return { currencies: [...currencies], bar_groups, stacks };
  }

  /** Whether this chart contains any stacks (or is just a single account). */
  get hasStackedData(): boolean {
    return this.accounts.length > 1;
  }

  /** The tooltip for a hovered account in the stacked bar chart. */
  tooltipTextAccount(
    c: FormatterContext,
    d: BarChartDatum,
    account: string,
    $chartToggledCurrencies: readonly string[],
  ): TooltipContent {
    const content = [];
    content.push(domHelpers.em(account));
    d.values.forEach(({ currency }) => {
      if (!$chartToggledCurrencies.includes(currency)) {
        const value = d.account_balances[account]?.[currency] ?? 0;
        content.push(domHelpers.t(c.amount(value, currency)));
        content.push(domHelpers.br());
      }
    });
    content.push(domHelpers.em(d.label));
    return content;
  }

  /** The tooltip for a hovered bar group in the bar chart. */
  tooltipText(c: FormatterContext, d: BarChartDatum): TooltipContent {
    const content = [];
    d.values.forEach((a) => {
      content.push(
        domHelpers.t(
          a.budget
            ? `${c.amount(a.value, a.currency)} / ${c.amount(
                a.budget,
                a.currency,
              )}`
            : c.amount(a.value, a.currency),
        ),
      );
      content.push(domHelpers.br());
    });
    content.push(domHelpers.em(d.label));
    return content;
  }
}

/** Get the currencies to use for the bar chart. */
function currencies_to_show(
  data: ParsedBarChartData,
  $chartContext: ChartContext,
): string[] {
  // Count the usage of each currency in the data.
  const counts = rollup(
    data.flatMap((interval) => [
      ...Object.keys(interval.budgets),
      ...Object.keys(interval.balance),
    ]),
    (v) => v.length,
    (r) => r,
  );

  // Show all operating currencies that are used in the data.
  const to_show = $chartContext.currencies.filter((c) => counts.delete(c));

  // Also add some of the most common other currencies (up to 5 in total)
  to_show.push(
    ...[...counts]
      .sort((a, b) => b[1] - a[1])
      .map((i) => i[0])
      .slice(0, Math.max(to_show.length, 5) - to_show.length),
  );

  return to_show;
}

/**
 * Try to parse a bar chart.
 */
export function bar(
  label: string | null,
  json: unknown,
  $chartContext: ChartContext,
): Result<BarChart, ValidationError> {
  return bar_validator(json).map((parsedData) => {
    const currencies = currencies_to_show(parsedData, $chartContext);

    const bar_groups = parsedData.map((interval) => ({
      values: currencies.map((currency) => ({
        currency,
        value: interval.balance[currency] ?? 0,
        budget: interval.budgets[currency] ?? 0,
      })),
      date: interval.date,
      label: $chartContext.dateFormat(interval.date),
      account_balances: interval.account_balances,
    }));

    return new BarChart(label, currencies, bar_groups);
  });
}
