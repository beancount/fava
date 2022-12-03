import { group } from "d3-array";

import { get } from "../../api";
import type { NamedFavaChart } from "../../charts";
import { _, format } from "../../i18n";
import { getURLFilters } from "../../stores/filters";

export const load = (url: URL) =>
  get("events", getURLFilters(url)).then((events) => {
    const groups = [...group(events, (e) => e.type)];

    const charts: NamedFavaChart[] = [
      { name: _("Events"), type: "scatterplot", data: events },
      ...groups.map(
        ([type, data]): NamedFavaChart => ({
          name: format(_("Event: %(type)s"), { type }),
          type: "scatterplot",
          data,
        })
      ),
    ];

    return { charts, groups };
  });

export type PageData = Awaited<ReturnType<typeof load>>;
