import { get_account_report } from "../../api/index.ts";
import type { AccountReportData } from "../../api/validators.ts";
import type { NonRelativeUrlPathError } from "../../helpers.ts";
import { get_url_path } from "../../helpers.ts";
import { err, ok, type Result } from "../../lib/result.ts";
import { get_url_filters } from "../../stores/filters.ts";
import { Route } from "../route.ts";
import AccountReport from "./AccountReport.svelte";

export type AccountReportType = "journal" | "balances" | "changes";

const to_report_type = (s: string | null): AccountReportType =>
  s === "balances" || s === "changes" ? s : "journal";

export interface AccountReportProps {
  account: string;
  report_type: AccountReportType;
  report: AccountReportData;
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
  return get_url_path(url).and_then((relative_path) => {
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
  async (url, signal) => {
    const account = get_account_from_url(url).unwrap();
    const report_type = to_report_type(url.searchParams.get("r"));
    const report = await get_account_report(
      { ...get_url_filters(url), a: account, r: report_type },
      signal,
    );

    return { account, report_type, report };
  },
  ({ account }) => `account:${account}`,
);
