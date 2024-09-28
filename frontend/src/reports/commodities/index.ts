import { get } from "../../api";
import type { FavaChart } from "../../charts";
import { LineChart } from "../../charts/line";
import { domHelpers } from "../../charts/tooltip";
import { day } from "../../format";
import { _ } from "../../i18n";
import { getURLFilters } from "../../stores/filters";
import { Route } from "../route";
import CommoditiesSvelte from "./Commodities.svelte";

export const commodities = new Route<{
  commodities: {
    base: string;
    quote: string;
    prices: [Date, number][];
  }[];
  charts: FavaChart[];
}>(
  "commodities",
  CommoditiesSvelte,
  async (url) =>
    get("commodities", getURLFilters(url)).then((cs) => {
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
