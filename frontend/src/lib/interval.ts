export type Interval = "year" | "quarter" | "month" | "week" | "day";

export const DEFAULT_INTERVAL: Interval = "month";

export function getInterval(s: string | null): Interval {
  if (s && ["year", "quarter", "month", "week", "day"].includes(s)) {
    return s as Interval;
  }
  return "month";
}
