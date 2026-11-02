import { _ } from "../i18n.ts";
import type { Validator } from "./validation.ts";
import { number, object } from "./validation.ts";

const INTERVALS = [
  "year",
  "fiscal_year",
  "quarter",
  "fiscal_quarter",
  "month",
  "week",
  "day",
] as const;

export type Interval = (typeof INTERVALS)[number];

export const DEFAULT_INTERVAL: Interval = "month";

/** Get the interval for a URL parameter value, falling back to the default. */
export function get_interval(s: string | null, fye: FiscalYearEnd): Interval {
  const intervals = fye.available_intervals;
  return intervals.includes(s as Interval) ? (s as Interval) : DEFAULT_INTERVAL;
}

/** Get the translatable label for an interval. */
export function interval_label(s: Interval): string {
  return {
    year: _("Yearly"),
    fiscal_year: _("Per Fiscal Year"),
    quarter: _("Quarterly"),
    fiscal_quarter: _("Per Fiscal Quarter"),
    month: _("Monthly"),
    week: _("Weekly"),
    day: _("Daily"),
  }[s];
}

/** The month and day on which a fiscal year ends. */
export class FiscalYearEnd {
  readonly month: number;
  readonly day: number;

  readonly available_intervals: readonly Interval[];

  #month_of_year: number;
  #year_offset: number;
  #start_month_of_year: number;
  #start_day: number;

  constructor(month: number, day: number) {
    this.month = month;
    this.day = day;
    this.#month_of_year = ((month - 1) % 12) + 1;
    this.#year_offset = Math.floor((month - 1) / 12);
    const start = new Date(Date.UTC(2001, this.#month_of_year - 1, day));
    start.setUTCDate(start.getUTCDate() + 1);
    this.#start_month_of_year = start.getUTCMonth() + 1;
    this.#start_day = start.getUTCDate();

    if (this.month === 12 && this.day === 31) {
      this.available_intervals = INTERVALS.filter(
        (i) => i !== "fiscal_year" && i !== "fiscal_quarter",
      );
    } else {
      this.available_intervals =
        this.#start_day === 1
          ? INTERVALS
          : INTERVALS.filter((i) => i !== "fiscal_quarter");
    }
  }

  /** The fiscal year (as in "FY2024") that a date falls into. */
  #fiscal_year(date: Date): number {
    const month = date.getUTCMonth() + 1;
    const day = date.getUTCDate();
    const after_start =
      month > this.#start_month_of_year ||
      (month === this.#start_month_of_year && day >= this.#start_day);
    const wraps = this.#start_month_of_year < this.#month_of_year;
    return (
      date.getUTCFullYear() +
      (after_start && !wraps ? 1 : 0) -
      this.#year_offset
    );
  }

  /** Format the date as a fiscal year (e.g. "FY2012") */
  format_year(date: Date): string {
    return `FY${this.#fiscal_year(date).toString()}`;
  }

  /** Format the date as a fiscal quarter (e.g. "FY2012-Q1") */
  format_quarter(date: Date): string {
    const month = date.getUTCMonth() + 1;
    const quarter =
      Math.floor(((month - this.#start_month_of_year + 12) % 12) / 3) + 1;
    return `FY${this.#fiscal_year(date).toString()}-Q${quarter.toString()}`;
  }

  /** Whether this fiscal year end is equal to another one. */
  equals(other: FiscalYearEnd): boolean {
    return this.month === other.month && this.day === other.day;
  }

  /** The default fiscal year end, matching the calendar year. */
  static default = new FiscalYearEnd(12, 31);

  private static raw_validator = object({ month: number, day: number });

  static validator: Validator<FiscalYearEnd> = (json) =>
    FiscalYearEnd.raw_validator(json).map(
      ({ month, day }) => new FiscalYearEnd(month, day),
    );
}
