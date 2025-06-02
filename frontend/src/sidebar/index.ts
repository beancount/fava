/**
 * This script initialises the AsideWithButton.svelte component.
 */

import { mount } from "svelte";
import { get as store_get } from "svelte/store";

import Modals from "../modals/Modals.svelte";
import { ledger_title } from "../stores/options";
import HeaderAndAside from "./HeaderAndAside.svelte";
import { page_title } from "./page-title";

export function initSidebar(): void {
  page_title.subscribe(({ title }) => {
    document.title = `${title} - ${store_get(ledger_title)}`;
  });

  const anchor = document.querySelector("article");
  mount(
    HeaderAndAside,
    anchor ? { target: document.body, anchor } : { target: document.body },
  );

  mount(Modals, {
    target: document.body,
  });
}
