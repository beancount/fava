/**
 * This script initialises the AsideWithButton.svelte component.
 */

import { get as store_get } from "svelte/store";

import Modals from "../modals/Modals.svelte";
import { ledger_title } from "../stores";
import HeaderAndAside from "./HeaderAndAside.svelte";
import { page_title } from "./page-title";

export function initSidebar(): void {
  page_title.subscribe(({ title }) => {
    document.title = `${title} - ${store_get(ledger_title)}`;
  });

  new HeaderAndAside({
    target: document.body,
    anchor: document.querySelector("article") ?? undefined,
  });

  new Modals({
    target: document.body,
  });
}
