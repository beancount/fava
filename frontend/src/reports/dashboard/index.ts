import { get_commodities, get_dashboard } from "../../api/index.ts";
import type { Commodities } from "../../api/validators.ts";
import type { ParsedFavaChart } from "../../charts/index.ts";
import { LineChart } from "../../charts/line.ts";
import { domHelpers } from "../../charts/tooltip.ts";
import { day } from "../../format.ts";
import { _ } from "../../i18n.ts";
import { getURLFilters } from "../../stores/filters.ts";
import { Route } from "../route.ts";
import Dashboard from "./Dashboard.svelte";

export interface DashboardReportProps {
  charts: ParsedFavaChart[];
  date_range: { begin: Date; end: Date } | null;
}

/**
 * Build a chart of the return (in percent, relative to the first known
 * price) of each commodity pair, so that holdings of different price
 * ranges can be compared on a single chart.
 */
function performance_chart(commodities: Commodities): LineChart | null {
  const series = commodities.flatMap(({ base, quote, prices }) => {
    const start = prices[0]?.[1];
    if (start == null || !start || prices.length < 2) {
      return [];
    }
    const name = `${base} / ${quote}`;
    const values = prices.map(([date, price]) => ({
      name,
      date,
      value: ((price - start) / start) * 100,
    }));
    return [{ name, values }];
  });
  if (!series.length) {
    return null;
  }
  return new LineChart(_("Performance"), series, (_c, d) => [
    `${d.name}: ${d.value.toFixed(2)}%`,
    domHelpers.em(day(d.date)),
  ]);
}

export const dashboard = new Route<DashboardReportProps>(
  "dashboard",
  Dashboard,
  async (url) => {
    const filters = getURLFilters(url);
    const [report, commodities] = await Promise.all([
      get_dashboard(filters),
      get_commodities(filters),
    ]);
    const performance = performance_chart(commodities);
    return {
      charts: performance ? [...report.charts, performance] : report.charts,
      date_range: report.date_range,
    };
  },
  () => _("Dashboard"),
);
