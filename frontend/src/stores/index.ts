import type { Writable } from "svelte/store";
import { derived, writable } from "svelte/store";

import type { BeancountError, LedgerData } from "../api/validators";
import type { Interval } from "../lib/interval";
import { DEFAULT_INTERVAL } from "../lib/interval";
import { derived_array } from "../lib/store";

export const urlHash = writable("");

export const conversion = writable("");
export const interval: Writable<Interval> = writable(DEFAULT_INTERVAL);

export const ledgerData = writable<LedgerData>();

/** Fava's options */
export const fava_options = derived(ledgerData, (val) => val.fava_options);
/** Beancount's options */
export const options = derived(ledgerData, (val) => val.options);
/** Beancount ledger title */
export const ledger_title = derived(ledgerData, (val) => val.options.title);
/** Commodity display precisions. */
export const precisions = derived(ledgerData, (val) => val.precisions);
/** Whether Fava supports exporting to Excel. */
export const HAVE_EXCEL = derived(ledgerData, (val) => val.have_excel);
/** Whether Fava should obscure all numbers. */
export const incognito = derived(ledgerData, (val) => val.incognito);
/** Base URL. */
export const base_url = derived(ledgerData, (val) => val.base_url);

/** The ranked array of all accounts. */
export const accounts = derived_array(ledgerData, (val) => val.accounts);

export const account_details = derived(
  ledgerData,
  (val) => val.account_details
);
/** The ranked array of all currencies. */
export const currencies = derived_array(ledgerData, (val) => val.currencies);
/** The ranked array of all links. */
export const links = derived_array(ledgerData, (val) => val.links);
/** The ranked array of all payees. */
export const payees = derived_array(ledgerData, (val) => val.payees);
/** The ranked array of all tags. */
export const tags = derived_array(ledgerData, (val) => val.tags);
/** The array of all years. */
export const years = derived_array(ledgerData, (val) => val.years);

/** The sorted array of operating currencies. */
export const operating_currency = derived_array(ledgerData, (val) =>
  val.options.operating_currency.sort()
);
/** The customized currency conversion select list */
export const conversion_currencies = derived_array(
  ledgerData,
  (val) => val.fava_options.conversion_currencies
);

/** The sorted array of all used currencies. */
export const currencies_sorted = derived_array(currencies, (val) =>
  [...val].sort()
);

/** The Beancount errors. */
export const errors = writable<BeancountError[]>([]);

export function closeOverlay(): void {
  if (window.location.hash) {
    window.history.pushState({}, "", "#");
  }
  urlHash.set("");
}
