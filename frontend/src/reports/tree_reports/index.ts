import {
  get_balance_sheet,
  get_income_statement,
  get_trial_balance,
} from "../../api/index.ts";
import type { AccountTreeNode } from "../../charts/hierarchy.ts";
import { _ } from "../../i18n.ts";
import { getURLFilters } from "../../stores/filters.ts";
import { Route } from "../route.ts";
import BalanceSheet from "./BalanceSheet.svelte";
import IncomeStatement from "./IncomeStatement.svelte";
import TrialBalance from "./TrialBalance.svelte";

export interface TreeReportProps {
  charts: unknown;
  trees: AccountTreeNode[];
  date_range: { begin: Date; end: Date } | null;
}

export const income_statement = new Route(
  "income_statement",
  IncomeStatement,
  async (url) => get_income_statement(getURLFilters(url)),
  () => _("Income Statement"),
);

export const balance_sheet = new Route(
  "balance_sheet",
  BalanceSheet,
  async (url) => get_balance_sheet(getURLFilters(url)),
  () => _("Balance Sheet"),
);

export const trial_balance = new Route(
  "trial_balance",
  TrialBalance,
  async (url) => get_trial_balance(getURLFilters(url)),
  () => _("Trial Balance"),
);
