import { rollup, sort } from "d3-array";
import type { Series } from "d3-shape";
import { stack, stackOffsetDiverging } from "d3-shape";

import type { FormatterContext } from "../format.ts";
import { ancestors } from "../lib/account.ts";
import type { ValidationT, Validator } from "../lib/validation.ts";
import {
  array,
  date,
  decimal,
  object,
  optional,
  record,
  string,
} from "../lib/validation.ts";
import type { ChartContext } from "./context.ts";
import type { ParsedFavaChart } from "./index.ts";
import type { TooltipContent } from "./tooltip.ts";
import { domHelpers } from "./tooltip.ts";

interface BarChartDatumValue {
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

interface FilteredBarChart {
  currencies: string[];
  bar_groups: BarChartDatum[];
  stacks: [currency: string, stacks: Series<BarChartDatum, string>[]][];
}

export class BarChart {
  readonly type = "barchart";
  /** The accounts that occur in some bar.  */
  readonly accounts: string[];
  readonly label: string | null;
  /** The currencies that are shown in this bar chart. */
  readonly currencies: readonly string[];
  /** The data for the (single) bars for all the intervals in this chart. */
  private readonly bar_groups: BarChartDatum[];

  constructor(
    label: string | null,
    currencies: readonly string[],
    bar_groups: BarChartDatum[],
  ) {
    this.label = label;
    this.currencies = currencies;
    this.bar_groups = bar_groups;
    this.accounts = sort(
      new Set(bar_groups.flatMap((d) => Object.keys(d.account_balances))),
    );
  }

  /** Filter the chart data and merge toggled accounts. */
  filter(
    hidden_names: ReadonlySet<string>,
    toggled_accounts: ReadonlySet<string>,
  ): FilteredBarChart {
    const currencies = this.currencies.filter((c) => !hidden_names.has(c));
    // Map each account to its topmost collapsed ancestor (or itself).
    const merged_account = new Map(
      this.accounts.map((account) => [
        account,
        ancestors(account).find((a) => toggled_accounts.has(a)) ?? account,
      ]),
    );
    const accounts = sort(new Set(merged_account.values()));
    const bar_groups = this.bar_groups.map((b) => {
      const account_balances: Record<string, Record<string, number>> = {};
      for (const [account, balance] of Object.entries(b.account_balances)) {
        const merged = merged_account.get(account) ?? account;
        account_balances[merged] ??= {};
        const merged_balance = account_balances[merged];
        for (const [currency, value] of Object.entries(balance)) {
          merged_balance[currency] = (merged_balance[currency] ?? 0) + value;
        }
      }
      return {
        ...b,
        values: b.values.filter((v) => !hidden_names.has(v.currency)),
        account_balances,
      };
    });
    const stacks = currencies.map(
      (currency): [string, Series<BarChartDatum, string>[]] => [
        currency,
        stack<BarChartDatum, string>()
          .keys(accounts)
          .value((d, account) => d.account_balances[account]?.[currency] ?? 0)
          .offset(stackOffsetDiverging)(bar_groups)
          .map((series) =>
            Object.assign(
              series.filter((b) => b[0] !== b[1] && !Number.isNaN(b[1])),
              { key: series.key, index: series.index },
            ),
          )
          .filter((series) => series.length > 0),
      ],
    );
    return { currencies, bar_groups, stacks };
  }

  /** Whether this chart contains any stacks (or is just a single account). */
  get has_stacked_data(): boolean {
    return this.accounts.length > 1;
  }

  /** The tooltip for a hovered account in the stacked bar chart. */
  tooltip_text_account(
    $ctx: FormatterContext,
    d: BarChartDatum,
    account: string,
    $chart_toggled_currencies_set: ReadonlySet<string>,
  ): TooltipContent {
    const content = [];
    content.push(domHelpers.em(account));
    d.values.forEach(({ currency }) => {
      if (!$chart_toggled_currencies_set.has(currency)) {
        const value = d.account_balances[account]?.[currency] ?? 0;
        content.push($ctx.amount(value, currency));
        content.push(domHelpers.br());
      }
    });
    content.push(domHelpers.em(d.label));
    return content;
  }

  /** The tooltip for a hovered bar group in the bar chart. */
  tooltip_text($ctx: FormatterContext, d: BarChartDatum): TooltipContent {
    const content = [];
    d.values.forEach(({ value, currency, budget }) => {
      content.push(
        budget
          ? `${$ctx.amount(value, currency)} / ${$ctx.amount(budget, currency)}`
          : $ctx.amount(value, currency),
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
  $chart_context: ChartContext,
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
  const to_show = $chart_context.currencies.filter((c) => counts.delete(c));

  // Also add some of the most common other currencies (up to 5 in total)
  to_show.push(
    ...[...counts]
      .sort((a, b) => b[1] - a[1])
      .map((i) => i[0])
      .slice(0, Math.max(to_show.length, 5) - to_show.length),
  );

  return to_show;
}

const bar_validator = array(
  object({
    date,
    budgets: record(decimal),
    balance: record(decimal),
    account_balances: record(record(decimal)),
  }),
);

type ParsedBarChartData = ValidationT<typeof bar_validator>;

const bar_chart_validator = object({
  label: string,
  key: optional(string),
  data: bar_validator,
});

export class ParsedBarChart implements ParsedFavaChart {
  readonly label: string | null;
  readonly data: ParsedBarChartData;
  readonly key: string | null;

  constructor(
    label: string | null,
    data: ParsedBarChartData,
    key: string | null = null,
  ) {
    this.label = label;
    this.data = data;
    this.key = key;
  }

  static validator: Validator<ParsedBarChart> = (json) =>
    bar_chart_validator(json).map(
      ({ label, data, key }) => new ParsedBarChart(label, data, key),
    );

  with_context($chart_context: ChartContext): BarChart {
    const currencies = currencies_to_show(this.data, $chart_context);

    const bar_groups = this.data.map((interval) => ({
      values: currencies.map((currency) => ({
        currency,
        value: interval.balance[currency] ?? 0,
        budget: interval.budgets[currency] ?? 0,
      })),
      date: interval.date,
      label: $chart_context.date_format(interval.date),
      account_balances: interval.account_balances,
    }));

    return new BarChart(this.label, currencies, bar_groups);
  }
}
