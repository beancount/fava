/**
 * This script initialises the AsideWithButton.svelte component.
 */

import FilterForm from "../header/FilterForm.svelte";
import Modals from "../modals/Modals.svelte";

import AsideWithButton from "./AsideWithButton.svelte";
import HeaderIcon from "./HeaderIcon.svelte";

export function initSidebar(): void {
  // eslint-disable-next-line no-new
  new AsideWithButton({
    target: document.body,
    anchor: document.querySelector("article") ?? undefined,
  });
  const header = document.querySelector("header");
  if (header) {
    // eslint-disable-next-line no-new
    new HeaderIcon({
      target: header,
      anchor: document.querySelector("h1") ?? undefined,
    });
    // eslint-disable-next-line no-new
    new FilterForm({
      target: header,
    });
  }
  // eslint-disable-next-line no-new
  new Modals({
    target: document.body,
  });
}
