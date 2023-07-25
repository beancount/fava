import { group } from "d3-array";

import { get } from "../../api";
import type { FavaChart } from "../../charts";
import { ScatterPlot } from "../../charts/scatterplot";
import { _, format } from "../../i18n";
import { getURLFilters } from "../../stores/filters";

export const load = (
  url: URL,
): Promise<{
  charts: FavaChart[];
  groups: [
    string,
    {
      type: string;
      description: string;
      date: Date;
    }[],
  ][];
}> =>
  get("events", getURLFilters(url)).then((events) => {
    const groups = [...group(events, (e) => e.type)];

    const charts = [
      new ScatterPlot(_("Events"), events),
      ...groups.map(
        ([type, data]) =>
          new ScatterPlot(format(_("Event: %(type)s"), { type }), data),
      ),
    ];

    return { charts, groups };
  });

export type PageData = Awaited<ReturnType<typeof load>>;
