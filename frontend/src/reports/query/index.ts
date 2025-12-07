import type { CodemirrorBql } from "../../codemirror/types.ts";
import { _ } from "../../i18n.ts";
import { Route } from "../route.ts";
import QuerySvelte from "./Query.svelte";

export interface QueryReportProps {
  codemirror_bql: CodemirrorBql;
}
export const query = new Route<QueryReportProps>(
  "query",
  QuerySvelte,
  async () => {
    const codemirror_bql = await import("../../codemirror/bql.ts");
    return { codemirror_bql };
  },
  () => _("Query"),
);
