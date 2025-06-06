import { get } from "../../api";
import type { Document } from "../../entries";
import { _ } from "../../i18n";
import { getURLFilters } from "../../stores/filters";
import { Route } from "../route";
import Documents from "./Documents.svelte";

export interface DocumentsReportProps {
  documents: Document[];
}

export const documents = new Route(
  "documents",
  Documents,
  async (url: URL) =>
    get("documents", getURLFilters(url)).then((data) => ({
      documents: data,
    })),
  () => _("Documents"),
);
