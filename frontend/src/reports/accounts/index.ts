import { get_account_report } from "../../api/index.ts";
import type { AccountBudget } from "../../api/validators.ts";
import type { AccountTreeNode } from "../../charts/hierarchy.ts";
import type { ParsedFavaChart } from "../../charts/index.ts";
import type { NonRelativeUrlPathError } from "../../helpers.ts";
import { getUrlPath } from "../../helpers.ts";
import { fragment_from_string } from "../../lib/dom.ts";
import { err, ok, type Result } from "../../lib/result.ts";
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

class NotAnAccountUrlError extends Error {
  constructor(pathname: string) {
    super(`Path '${pathname}' is not a path for the account report.`);
  }
}

/**
 * Get the account from the given URL.
 */
export function get_account_from_url(
  url: URL,
): Result<string, NonRelativeUrlPathError | NotAnAccountUrlError> {
  return getUrlPath(url).and_then((relative_path) => {
    const [base, account] = relative_path.split("/");
    if (base === "account" && account != null) {
      return ok(account);
    }
    return err(new NotAnAccountUrlError(relative_path));
  });
}

export const account_report = new Route<AccountReportProps>(
  "account",
  AccountReport,
  async (url) => {
    const account = get_account_from_url(url).unwrap();
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
