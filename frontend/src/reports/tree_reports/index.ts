import { get } from "../../api";
import { _ } from "../../i18n";
import { getURLFilters } from "../../stores/filters";
import { Route } from "../route";
import BalanceSheet from "./BalanceSheet.svelte";
import IncomeStatement from "./IncomeStatement.svelte";
import TrialBalance from "./TrialBalance.svelte";

export const income_statement = new Route(
  "income_statement",
  IncomeStatement,
  async (url) => get("income_statement", getURLFilters(url)),
  () => _("Income Statement"),
);

export const balance_sheet = new Route(
  "balance_sheet",
  BalanceSheet,
  async (url) => get("balance_sheet", getURLFilters(url)),
  () => _("Balance Sheet"),
);

export const trial_balance = new Route(
  "trial_balance",
  TrialBalance,
  async (url) => get("trial_balance", getURLFilters(url)),
  () => _("Trial Balance"),
);
