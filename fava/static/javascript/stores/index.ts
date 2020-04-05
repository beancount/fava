import { Readable, derived, writable, Writable } from "svelte/store";

import {
  object,
  array,
  string,
  boolean,
  number,
  union,
  constant,
} from "../lib/validation";
import { shallow_equal } from "../lib/equals";

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
  years: array(string),
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

function derived_array<S, T>(
  store: Readable<S>,
  getter: (values: S) => T[]
): Readable<T[]> {
  let val: T[] = [];
  return derived(
    store,
    (store_val, set) => {
      const newVal = getter(store_val);
      if (!shallow_equal(val, newVal)) {
        set(newVal);
        val = newVal;
      }
    },
    val
  );
}

export const accounts = derived_array(favaAPIStore, val => val.accounts);
export const currencies = derived_array(favaAPIStore, val => val.currencies);
export const links = derived_array(favaAPIStore, val => val.links);
export const payees = derived_array(favaAPIStore, val => val.payees);
export const tags = derived_array(favaAPIStore, val => val.tags);
export const years = derived_array(favaAPIStore, val => val.years);

export const operating_currency = derived_array(favaAPIStore, val =>
  val.options.operating_currency.sort()
);

export const commodities = derived_array(favaAPIStore, val =>
  val.options.commodities.sort()
);

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
