import { get } from "../../api";
import type { AccountBudget } from "../../api/validators";
import type { AccountTreeNode } from "../../charts/hierarchy";
import { getUrlPath } from "../../helpers";
import { getURLFilters } from "../../stores/filters";
import { Route } from "../route";
import AccountReport from "./AccountReport.svelte";

export type AccountReportType = "journal" | "balances" | "changes";

const to_report_type = (s: string | null): AccountReportType =>
  s === "balances" || s === "changes" ? s : "journal";

export interface AccountReportProps {
  account: string;
  report_type: AccountReportType;
  charts: unknown;
  journal: string | null;
  interval_balances: AccountTreeNode[] | null;
  dates: { begin: Date; end: Date }[] | null;
  budgets: Record<string, AccountBudget[]> | null;
}

export const account_report = new Route<AccountReportProps>(
  "account",
  AccountReport,
  async (url) => {
    const [, account = ""] = getUrlPath(url)?.split("/") ?? [];
    const report_type = to_report_type(url.searchParams.get("r"));
    const res = await get("account_report", {
      ...getURLFilters(url),
      a: account,
      r: report_type,
    });
    return { ...res, account, report_type };
  },
  (route) => {
    if (route.url) {
      const [, account] = getUrlPath(route.url)?.split("/") ?? [];
      return `account:${account ?? "ERROR"}`;
    }
    throw new Error("Internal error: Expected route to have URL.");
  },
);
