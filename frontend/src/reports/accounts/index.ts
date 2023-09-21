import { get } from "../../api";
import { getUrlPath } from "../../helpers";
import { getURLFilters } from "../../stores/filters";
import { Route } from "../route";

import AccountReport from "./AccountReport.svelte";

export type AccountReportType = "journal" | "balances" | "changes";

const to_report_type = (s: string | null): AccountReportType =>
  s === "balances" || s === "changes" ? s : "journal";

export const account_report = new Route(
  "account",
  AccountReport,
  async (url) => {
    let path = getUrlPath(url);
    if (path) {
      // prevent decodeURI from turning null into "null"
      path = decodeURI(path);
    }
    const [, account = ""] = path?.split("/") ?? [];

    const report_type = to_report_type(url.searchParams.get("r"));
    const res = await get("account_report", {
      ...getURLFilters(url),
      a: account,
      r: report_type,
    });
    return {
      ...res,
      account,
      report_type: to_report_type(report_type),
    };
  },
  (route) => {
    if (route.url) {
      let path = getUrlPath(route.url);
      if (path) {
        // prevent decodeURI from turning null into "null"
        path = decodeURI(path);
      }
      const [, account] = path?.split("/") ?? [];
      return `account:${account}`;
    }
    throw new Error("Internal error: Expected route to have URL.");
  },
);
