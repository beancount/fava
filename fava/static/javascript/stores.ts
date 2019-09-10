import { writable, Writable } from "svelte/store";

import {
  object,
  array,
  string,
  boolean,
  number,
  union,
  constant,
} from "./validation";

export const urlHash = writable("");

export const conversion = writable("");
type Interval = "year" | "quarter" | "month" | "week" | "day";
export const interval: Writable<Interval> = writable("month");
export const showCharts = writable(true);

export const activeChart = writable({});
export const chartMode = writable("treemap");
export const chartCurrency = writable("");

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
    interval: string,
    locale: union(string, constant(null)),
  }),
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

export const favaAPI = favaAPIValidator({
  accountURL: "",
  accounts: [],
  baseURL: "",
  currencies: [],
  documentTitle: "",
  errors: 0,
  favaOptions: {
    "auto-reload": false,
    "currency-column": 80,
    interval: "month",
    locale: null,
  },
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
});

export type FavaAPI = typeof favaAPI;

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

export function closeOverlay() {
  if (window.location.hash) {
    window.history.pushState({}, "", "#");
  }
  urlHash.set("");
}
