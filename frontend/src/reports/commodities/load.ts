import { get } from "../../api";
import type { NamedFavaChart } from "../../charts";
import { domHelpers } from "../../charts/tooltip";
import { day } from "../../format";
import { getURLFilters } from "../../stores/filters";

export const load = (url: URL) =>
  get("commodities", getURLFilters(url)).then((commodities) => {
    const charts: NamedFavaChart[] = commodities.map(
      ({ base, quote, prices }) => {
        const name = `${base} / ${quote}`;
        const values = prices.map((d) => ({ name, date: d[0], value: d[1] }));

        return {
          name,
          type: "linechart",
          data: [{ name, values }],
          tooltipText: (c, d) => [
            domHelpers.t(`1 ${base} = ${c.amount(d.value, quote)}`),
            domHelpers.em(day(d.date)),
          ],
        };
      }
    );
    return { commodities, charts };
  });

export type PageData = Awaited<ReturnType<typeof load>>;
