import type { Readable, Writable } from "svelte/store";
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
  record,
  string,
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
    })
  ),
  baseURL: string,
  currencies: array(string),
  errors: number,
  favaOptions: object({
    auto_reload: boolean,
    currency_column: number,
    indent: number,
    locale: union(string, constant(null)),
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
  }),
  payees: array(string),
  tags: array(string),
  years: array(string),
});

export const rawLedgerData = writable("");

type LedgerData = ValidationT<typeof ledgerDataValidator>;

export const ledgerData: Readable<LedgerData> = derived(rawLedgerData, (s) => {
  const res = ledgerDataValidator(JSON.parse(s));
  if (!res.success) {
    // TODO log error
    throw new Error("Loading ledger data failed.");
  }
  return res.value;
});

/** Fava's options */
export const favaOptions = derived(ledgerData, (val) => val.favaOptions);
/** Beancount's options */
export const options = derived(ledgerData, (val) => val.options);
/** Whether Fava supports exporting to Excel. */
export const HAVE_EXCEL = derived(ledgerData, (val) => val.have_excel);
/** Whether Fava should obscure all numbers. */
export const incognito = derived(ledgerData, (val) => val.incognito);
/** Base URL. */
export const baseURL = derived(ledgerData, (val) => val.baseURL);

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
