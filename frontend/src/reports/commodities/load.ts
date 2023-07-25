import { get } from "../../api";
import type { FavaChart } from "../../charts";
import { LineChart } from "../../charts/line";
import { domHelpers } from "../../charts/tooltip";
import { day } from "../../format";
import { getURLFilters } from "../../stores/filters";

export const load = (
  url: URL,
): Promise<{
  commodities: {
    base: string;
    quote: string;
    prices: [Date, number][];
  }[];
  charts: FavaChart[];
}> =>
  get("commodities", getURLFilters(url)).then((commodities) => {
    const charts = commodities.map(({ base, quote, prices }) => {
      const name = `${base} / ${quote}`;
      const values = prices.map((d) => ({ name, date: d[0], value: d[1] }));

      return new LineChart(name, [{ name, values }], (c, d) => [
        domHelpers.t(`1 ${base} = ${c.amount(d.value, quote)}`),
        domHelpers.em(day(d.date)),
      ]);
    });
    return { commodities, charts };
  });

export type PageData = Awaited<ReturnType<typeof load>>;
