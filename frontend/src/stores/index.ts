import { derived, Readable, writable, Writable } from "svelte/store";

import { derived_array } from "../lib/store";
import {
  array,
  boolean,
  constant,
  number,
  object,
  string,
  union,
} from "../lib/validation";

export const urlHash = writable("");

export const conversion = writable("");
type Interval = "year" | "quarter" | "month" | "week" | "day";
export const interval: Writable<Interval> = writable("month");

export const ledgerDataValidator = object({
  accounts: array(string),
  baseURL: string,
  currencies: array(string),
  errors: number,
  favaOptions: object({
    "auto-reload": boolean,
    "currency-column": number,
    conversion: string,
    indent: number,
    interval: string,
    locale: union(string, constant(null)),
    "insert-entry": array(
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

type LedgerData = ReturnType<typeof ledgerDataValidator>;

export const ledgerData: Readable<LedgerData> = derived(rawLedgerData, (s) =>
  ledgerDataValidator(JSON.parse(s))
);

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

/**
 * The list of operating currencies, adding in the current conversion currency.
 */
export const operatingCurrenciesWithConversion = derived(
  [operating_currency, conversion],
  ([operating_currency_val, conversion_val]) => {
    if (
      !conversion_val ||
      ["at_cost", "at_value", "units"].includes(conversion_val) ||
      operating_currency_val.includes(conversion_val)
    ) {
      return operating_currency_val;
    }
    return [...operating_currency_val, conversion_val];
  }
);

/** The number of Beancount errors. */
export const errorCount = writable(0);

export function closeOverlay(): void {
  if (window.location.hash) {
    window.history.pushState({}, "", "#");
  }
  urlHash.set("");
}
