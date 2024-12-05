import { get } from "../../api";
import { _ } from "../../i18n";
import { getURLFilters } from "../../stores/filters";
import { Route } from "../route";
import Documents from "./Documents.svelte";

export const documents = new Route(
  "documents",
  Documents,
  async (url: URL) =>
    get("documents", getURLFilters(url)).then((data) => ({
      documents: data,
    })),
  () => _("Documents"),
);
