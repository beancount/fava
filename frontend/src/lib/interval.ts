import { _ } from "../i18n";

export type Interval = "year" | "quarter" | "month" | "week" | "day";

export const DEFAULT_INTERVAL: Interval = "month";

export const INTERVALS: Interval[] = [
  "year",
  "quarter",
  "month",
  "week",
  "day",
];

export function getInterval(s: string | null): Interval {
  if (s && INTERVALS.includes(s as Interval)) {
    return s as Interval;
  }
  return DEFAULT_INTERVAL;
}

/** Get the translateable label for an interval. */
export function intervalLabel(s: Interval): string {
  return {
    year: _("Yearly"),
    quarter: _("Quarterly"),
    month: _("Monthly"),
    week: _("Weekly"),
    day: _("Daily"),
  }[s];
}
