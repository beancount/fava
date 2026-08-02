import { get_documents } from "../../api/index.ts";
import type { Document } from "../../entries/index.ts";
import { _ } from "../../i18n.ts";
import { get_url_filters } from "../../stores/filters.ts";
import { Route } from "../route.ts";
import Documents from "./Documents.svelte";

export interface DocumentsReportProps {
  documents: Document[];
}

export const documents = new Route(
  "documents",
  Documents,
  async (url: URL) =>
    get_documents(get_url_filters(url)).then((data) => ({
      documents: data,
    })),
  () => _("Documents"),
);
