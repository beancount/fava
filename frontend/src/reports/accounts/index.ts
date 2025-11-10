import { get_account_report } from "../../api/index.ts";
import type { AccountBudget } from "../../api/validators.ts";
import type { AccountTreeNode } from "../../charts/hierarchy.ts";
import type { ParsedFavaChart } from "../../charts/index.ts";
import { getUrlPath } from "../../helpers.ts";
import { fragment_from_string } from "../../lib/dom.ts";
import { getURLFilters } from "../../stores/filters.ts";
import { Route } from "../route.ts";
import AccountReport from "./AccountReport.svelte";

export type AccountReportType = "journal" | "balances" | "changes";

const to_report_type = (s: string | null): AccountReportType =>
  s === "balances" || s === "changes" ? s : "journal";

export interface AccountReportProps {
  account: string;
  report_type: AccountReportType;
  charts: ParsedFavaChart[];
  journal: DocumentFragment | null;
  interval_balances: AccountTreeNode[] | null;
  dates: { begin: Date; end: Date }[] | null;
  budgets: Record<string, AccountBudget[]> | null;
}

export const account_report = new Route<AccountReportProps>(
  "account",
  AccountReport,
  async (url) => {
    const [, account = ""] = getUrlPath(url).unwrap().split("/");
    const report_type = to_report_type(url.searchParams.get("r"));
    const { charts, journal, interval_balances, dates, budgets } =
      await get_account_report({
        ...getURLFilters(url),
        a: account,
        r: report_type,
      });

    return {
      charts,
      journal: journal != null ? fragment_from_string(journal) : null,
      interval_balances,
      dates,
      budgets,
      account,
      report_type,
    };
  },
  (url) => {
    const [, account] = getUrlPath(url).unwrap().split("/");
    return `account:${account ?? "ERROR"}`;
  },
);
