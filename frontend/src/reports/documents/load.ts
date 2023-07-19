import { get } from "../../api";
import { getURLFilters } from "../../stores/filters";

export const load = (
  url: URL,
): Promise<{
  data: {
    account: string;
    filename: string;
    date: string;
  }[];
}> =>
  get("documents", getURLFilters(url)).then((data) => ({
    data,
  }));

export type PageData = Awaited<ReturnType<typeof load>>;
