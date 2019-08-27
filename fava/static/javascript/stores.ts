import { writable } from "svelte/store";

import {
  Validator,
  object,
  array,
  string,
  boolean,
  record,
  number,
  union,
  constant,
} from "./validation";

export const urlHash = writable("");

export const conversion = writable("");
export const interval = writable("");
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
    operating_currency: array(string),
  }),
  pageTitle: string,
  payees: array(string),
  tags: array(string),
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
    operating_currency: [],
  },
  tags: [],
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
