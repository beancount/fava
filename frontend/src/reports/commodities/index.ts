import { get_commodities } from "../../api/index.ts";
import type { Commodities } from "../../api/validators.ts";
import { LineChart } from "../../charts/line.ts";
import { domHelpers } from "../../charts/tooltip.ts";
import { day } from "../../format.ts";
import { _ } from "../../i18n.ts";
import { getURLFilters } from "../../stores/filters.ts";
import { Route } from "../route.ts";
import CommoditiesSvelte from "./Commodities.svelte";

export interface CommoditiesReportProps {
  charts: LineChart[];
  commodities: Commodities;
}

export const commodities = new Route<CommoditiesReportProps>(
  "commodities",
  CommoditiesSvelte,
  async (url) =>
    get_commodities(getURLFilters(url)).then((cs) => {
      const charts = cs.map(({ base, quote, prices }) => {
        const name = `${base} / ${quote}`;
        const values = prices.map((d) => ({ name, date: d[0], value: d[1] }));

        return new LineChart(name, [{ name, values }], (c, d) => [
          domHelpers.t(`1 ${base} = ${c.amount(d.value, quote)}`),
          domHelpers.em(day(d.date)),
        ]);
      });
      return { commodities: cs, charts };
    }),
  () => _("Commodities"),
);
