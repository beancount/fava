import type { Writable } from "svelte/store";
import { derived, writable } from "svelte/store";

import type { Interval } from "../lib/interval";
import { DEFAULT_INTERVAL } from "../lib/interval";
import { derived_array } from "../lib/store";
import type { ValidationT } from "../lib/validation";
import {
  array,
  boolean,
  constant,
  date,
  number,
  object,
  optional,
  record,
  string,
  tuple,
  union,
} from "../lib/validation";

export const urlHash = writable("");

export const conversion = writable("");
export const interval: Writable<Interval> = writable(DEFAULT_INTERVAL);

export const ledgerDataValidator = object({
  accounts: array(string),
  account_details: record(
    object({
      close_date: date,
      uptodate_status: optional(string),
      last_entry: optional(object({ date, entry_hash: string })),
      balance_string: optional(string),
    })
  ),
  base_url: string,
  currencies: array(string),
  errors: number,
  fava_options: object({
    auto_reload: boolean,
    currency_column: number,
    conversion_currencies: array(string),
    import_config: optional(string),

    indent: number,
    locale: union(string, constant(null)),
    uptodate_indicator_grey_lookback_days: number,
    insert_entry: array(
      object({ date: string, filename: string, lineno: number, re: string })
    ),
  }),
  have_excel: boolean,
  incognito: boolean,
  links: array(string),
  options: object({
    documents: array(string),
    filename: string,
    include: array(string),
    operating_currency: array(string),
    title: string,
  }),
  payees: array(string),
  precisions: record(number),
  tags: array(string),
  years: array(string),
  user_queries: array(object({ name: string, query_string: string })),
  upcoming_events_count: number,
  extension_reports: array(tuple([string, string])),
  sidebar_links: array(tuple([string, string])),
  other_ledgers: array(tuple([string, string])),
});

type LedgerData = ValidationT<typeof ledgerDataValidator>;

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

/** The number of Beancount errors. */
export const errorCount = writable(0);

export function closeOverlay(): void {
  if (window.location.hash) {
    window.history.pushState({}, "", "#");
  }
  urlHash.set("");
}
