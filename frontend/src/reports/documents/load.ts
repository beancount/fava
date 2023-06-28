import { get } from "../../api";
import { getURLFilters } from "../../stores/filters";

export const load = (url: URL) =>
  get("documents", getURLFilters(url)).then((data) => ({
    data,
  }));

export type PageData = Awaited<ReturnType<typeof load>>;
