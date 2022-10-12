/**
 * This script updates the links and error count in the sidebar as well as
 * toggling the sidebar on mobile.
 */

import { errorCount } from "../stores";

export function updateSidebar(): void {
  document.querySelectorAll("aside a").forEach((el) => {
    el.classList.remove("selected");
    const href = el.getAttribute("href");
    if (
      !el.hasAttribute("data-remote") &&
      href?.includes(window.location.pathname) &&
      !el.matches(".submenu a")
    ) {
      el.classList.add("selected");
    }
  });
}

function initErrorCount(): void {
  const el = document.getElementById("error-count");
  if (el instanceof HTMLLIElement) {
    errorCount.subscribe((count) => {
      el.classList.toggle("hidden", count === 0);
      const span = el.querySelector("span");
      if (span) {
        span.textContent = `${count}`;
      }
    });
  }
}

function initAsideButton(): void {
  const el = document.getElementById("aside-button");
  if (el instanceof HTMLButtonElement) {
    el.addEventListener("click", () => {
      document.querySelector("aside")?.classList.toggle("active");
      el.classList.toggle("active");
    });
  }
}

export function initSidebar(): void {
  initErrorCount();
  initAsideButton();
}
