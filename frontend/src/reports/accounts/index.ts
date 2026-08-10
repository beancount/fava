import { get_account_report } from "../../api/index.ts";
import type { AccountBudget } from "../../api/validators.ts";
import type { AccountTreeNode } from "../../charts/hierarchy.ts";
import type { ParsedFavaChart } from "../../charts/index.ts";
import type { NonRelativeUrlPathError } from "../../helpers.ts";
import { getUrlPath } from "../../helpers.ts";
import { fragment_from_string } from "../../lib/dom.ts";
import { err, ok, type Result } from "../../lib/result.ts";
import { log_error } from "../../log.ts";
import { notify_err } from "../../notifications.ts";
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
  load_page: ((page: number) => Promise<DocumentFragment | null>) | null;
  total_pages: number;
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
    const filters = getURLFilters(url);
    const { charts, journal, total_pages, interval_balances, dates, budgets } =
      await get_account_report({
        ...filters,
        a: account,
        r: report_type,
        page: 1,
      });

    let error_shown = false;
    const load_page = async (page: number) => {
      return get_account_report({
        ...filters,
        a: account,
        r: report_type,
        page,
      }).then(
        (res) =>
          res.journal != null ? fragment_from_string(res.journal) : null,
        (error: unknown) => {
          log_error(
            `Failed to fetch account journal page ${page.toString()}`,
            error,
          );
          if (!error_shown) {
            notify_err(new Error("Failed to fetch some account journal pages"));
            error_shown = true;
          }
          return null;
        },
      );
    };

    return {
      charts,
      journal: journal != null ? fragment_from_string(journal) : null,
      load_page: journal != null ? load_page : null,
      total_pages: journal != null ? (total_pages ?? 1) : 1,
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
