import { derived, writable, Writable } from "svelte/store";

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

import { baseURL } from "./url";

export const urlHash = writable("");

export const conversion = writable("");
type Interval = "year" | "quarter" | "month" | "week" | "day";
export const interval: Writable<Interval> = writable("month");

export const favaAPIValidator = object({
  accounts: array(string),
  baseURL: string,
  currencies: array(string),
  documentTitle: string,
  errors: number,
  favaOptions: object({
    "auto-reload": boolean,
    "currency-column": number,
    conversion: string,
    interval: string,
    locale: union(string, constant(null)),
  }),
  have_excel: boolean,
  incognito: boolean,
  links: array(string),
  options: object({
    documents: array(string),
    operating_currency: array(string),
  }),
  pageTitle: string,
  payees: array(string),
  tags: array(string),
  years: array(string),
});

export type FavaAPI = ReturnType<typeof favaAPIValidator>;
export const favaAPI: FavaAPI = {
  accounts: [],
  baseURL: "",
  currencies: [],
  documentTitle: "",
  errors: 0,
  favaOptions: {
    "auto-reload": false,
    "currency-column": 80,
    conversion: "at_cost",
    interval: "month",
    locale: null,
  },
  have_excel: false,
  incognito: false,
  links: [],
  pageTitle: "",
  payees: [],
  options: {
    documents: [],
    operating_currency: [],
  },
  tags: [],
  years: [],
};

export const favaAPIStore = writable(favaAPI);

/** Whether Fava supports exporting to Excel. */
export const HAVE_EXCEL = derived(favaAPIStore, (val) => val.have_excel);
/** The ranked array of all accounts. */
export const accounts = derived_array(favaAPIStore, (val) => val.accounts);
/** The ranked array of all currencies. */
export const currencies = derived_array(favaAPIStore, (val) => val.currencies);
/** The ranked array of all links. */
export const links = derived_array(favaAPIStore, (val) => val.links);
/** The ranked array of all payees. */
export const payees = derived_array(favaAPIStore, (val) => val.payees);
/** The ranked array of all tags. */
export const tags = derived_array(favaAPIStore, (val) => val.tags);
/** The array of all years. */
export const years = derived_array(favaAPIStore, (val) => val.years);

/** The sorted array of operating currencies. */
export const operating_currency = derived_array(favaAPIStore, (val) =>
  val.options.operating_currency.sort()
);

/** The sorted array of all used currencies. */
export const currencies_sorted = derived_array(currencies, (val) =>
  [...val].sort()
);

/** The number of Beancount errors. */
export const errorCount = writable(0);

favaAPIStore.subscribe((val) => {
  Object.assign(favaAPI, val);
  errorCount.set(favaAPI.errors);
  baseURL.set(favaAPI.baseURL);
});

/**
 * Get the list of completions for the given type of entry attribute.
 */
export function getCompletion(
  type: "accounts" | "currencies" | "links" | "tags"
): string[] {
  return favaAPI[type];
}

export function closeOverlay(): void {
  if (window.location.hash) {
    window.history.pushState({}, "", "#");
  }
  urlHash.set("");
}
