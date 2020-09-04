/**
 * This script updates the links and error count in the sidebar as well as
 * toggling the sidebar on mobile.
 */

import { errorCount } from "../stores";
import AccountSelectorSvelte from "./AccountSelector.svelte";

export function updateSidebar(): void {
  document.querySelectorAll("aside a").forEach((el) => {
    el.classList.remove("selected");
    const href = el.getAttribute("href");
    if (
      !el.hasAttribute("data-remote") &&
      href?.includes(window.location.pathname)
    ) {
      el.classList.add("selected");
    }
  });
}

export class AccountSelector extends HTMLLIElement {
  component?: AccountSelectorSvelte;

  connectedCallback(): void {
    this.component = new AccountSelectorSvelte({ target: this });
  }

  disconnectedCallback(): void {
    this.component?.$destroy();
    this.component = undefined;
  }
}

export class ErrorCount extends HTMLLIElement {
  constructor() {
    super();

    errorCount.subscribe((errorCount_val) => {
      this.classList.toggle("hidden", errorCount_val === 0);
      const span = this.querySelector("span");
      if (span) {
        span.innerHTML = `${errorCount_val}`;
      }
    });
  }
}

export class AsideButton extends HTMLButtonElement {
  constructor() {
    super();

    this.addEventListener("click", () => {
      document.querySelector("aside")?.classList.toggle("active");
      this.classList.toggle("active");
    });
  }
}
