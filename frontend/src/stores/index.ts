import { derived, type Readable, writable } from "svelte/store";

import type { BeancountError, LedgerData } from "../api/validators";
import { get_internal_accounts } from "../lib/account";
import { DEFAULT_INTERVAL } from "../lib/interval";
import { derived_array } from "../lib/store";

/** The current conversion used for reports. */
export const conversion = writable("");
/** The current interval used for reports. */
export const interval = writable(DEFAULT_INTERVAL);

/** The Beancount errors. */
export const errors = writable<readonly BeancountError[]>([]);

export const ledgerData = writable<LedgerData>();

/** Commodity display precisions. */
export const precisions = derived(ledgerData, (v) => v.precisions);
/** Whether Fava supports exporting to Excel. */
export const HAVE_EXCEL = derived(ledgerData, (v) => v.have_excel);
/** Whether Fava should obscure all numbers. */
export const incognito = derived(ledgerData, (v) => v.incognito);
/** Base URL. */
export const base_url = derived(ledgerData, (v) => v.base_url);
/** The Fava extensions. */
export const extensions = derived(ledgerData, (v) => v.extensions);

/** The ranked array of all accounts. */
export const accounts = derived_array(ledgerData, (v) => v.accounts);
export const accounts_set: Readable<ReadonlySet<string>> = derived(
  accounts,
  ($accounts) => new Set($accounts),
);
/** All non-leaf accounts. */
export const accounts_internal = derived_array(accounts, get_internal_accounts);

/** Get the name (as given per metadata) of a currency. */
export const currency_name = derived(
  ledgerData,
  ({ currency_names }) =>
    (c: string) =>
      currency_names[c] ?? c,
);

/** Account information. */
export const account_details = derived(ledgerData, (v) => v.account_details);
/** The ranked array of all currencies. */
export const currencies = derived_array(ledgerData, (v) => v.currencies);
/** The ranked array of all links. */
export const links = derived_array(ledgerData, (v) => v.links);
/** The ranked array of all payees. */
export const payees = derived_array(ledgerData, (v) => v.payees);
/** The ranked array of all tags. */
export const tags = derived_array(ledgerData, (v) => v.tags);
/** The array of all years. */
export const years = derived_array(ledgerData, (v) => v.years);

/** The sorted array of all used currencies. */
export const currencies_sorted = derived_array(currencies, ($currencies) =>
  $currencies.toSorted(),
);
