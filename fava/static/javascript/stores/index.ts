import { writable, Writable } from "svelte/store";

import {
  object,
  array,
  string,
  boolean,
  number,
  union,
  constant,
} from "../validation";

export const urlHash = writable("");

export const conversion = writable("");
type Interval = "year" | "quarter" | "month" | "week" | "day";
export const interval: Writable<Interval> = writable("month");

export const favaAPIValidator = object({
  accountURL: string,
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
    commodities: array(string),
    documents: array(string),
    operating_currency: array(string),
  }),
  pageTitle: string,
  payees: array(string),
  tags: array(string),
  years: array(number),
});

export type FavaAPI = ReturnType<typeof favaAPIValidator>;
export const favaAPI: FavaAPI = {
  accountURL: "",
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
    commodities: [],
    documents: [],
    operating_currency: [],
  },
  tags: [],
  years: [],
};

export const favaAPIStore = writable(favaAPI);
favaAPIStore.subscribe(val => {
  Object.assign(favaAPI, val);
});

export const filters = writable({
  time: "",
  filter: "",
  account: "",
});

export const urlSyncedParams = [
  "account",
  "charts",
  "conversion",
  "filter",
  "interval",
  "time",
];

/** Url for the account page for an account. */
export function accountUrl(account: string): string {
  return new URL(
    favaAPI.accountURL.replace("REPLACEME", account),
    window.location.href
  ).toString();
}

export function closeOverlay(): void {
  if (window.location.hash) {
    window.history.pushState({}, "", "#");
  }
  urlHash.set("");
}
