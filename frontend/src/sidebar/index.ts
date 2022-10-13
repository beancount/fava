/**
 * This script initialises the AsideWithButton.svelte component.
 */

import AsideWithButton from "./AsideWithButton.svelte";

export function initSidebar(): void {
  // eslint-disable-next-line no-new
  new AsideWithButton({
    target: document.body,
    anchor: document.querySelector("article") ?? undefined,
  });
}
