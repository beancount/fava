import Mousetrap from "mousetrap";

import { select, selectAll, once } from "./helpers";
import e from "./events";
import { closeOverlay } from "./stores";

function click(selector: string) {
  const element = select(selector);
  if (element && element instanceof HTMLElement) {
    element.click();
  }
}

e.on("page-loaded", () => {
  selectAll("[data-key]").forEach(element => {
    const key = element.getAttribute("data-key");
    if (key !== null) {
      Mousetrap.bind(
        key,
        () => {
          const tag = element.tagName;
          if (tag === "BUTTON" || tag === "A") {
            (element as HTMLButtonElement | HTMLAnchorElement).click();
          } else if (tag === "INPUT") {
            (element as HTMLInputElement).focus();
          }
        },
        "keyup"
      );
    }
  });
});

// Add a tooltip showing the keyboard shortcut over the target element.
function showTooltip(target: HTMLElement) {
  const tooltip = document.createElement("div");
  tooltip.className = "keyboard-tooltip";
  tooltip.innerHTML = target.getAttribute("data-key") || "";
  document.body.appendChild(tooltip);
  const parentCoords = target.getBoundingClientRect();
  // Padded 10px to the left if there is space or centered otherwise
  const left =
    parentCoords.left +
    Math.min((target.offsetWidth - tooltip.offsetWidth) / 2, 10);
  const top =
    parentCoords.top + (target.offsetHeight - tooltip.offsetHeight) / 2;
  tooltip.style.left = `${left}px`;
  tooltip.style.top = `${top + window.pageYOffset}px`;
}

// Show all keyboard shortcut tooltips.
function showTooltips() {
  const reloadButton = select("#reload-page");
  if (reloadButton) {
    reloadButton.classList.remove("hidden");
  }
  selectAll("[data-key]").forEach(el => {
    showTooltip(el as HTMLElement);
  });
}

// Remove all keyboard shortcut tooltips.
function removeTooltips() {
  const reloadButton = select("#reload-page");
  if (reloadButton) {
    reloadButton.classList.add("hidden");
  }
  selectAll(".keyboard-tooltip").forEach(tooltip => {
    tooltip.remove();
  });
}

e.on("page-init", () => {
  Mousetrap.bind("?", () => {
    removeTooltips();
    showTooltips();
    once(document, "mousedown", () => {
      removeTooltips();
    });
  });

  Mousetrap.bind("esc", () => {
    closeOverlay();
    removeTooltips();
  });

  // Charts
  Mousetrap.bind("c", () => {
    const selected = select(".chart-labels .selected");

    if (selected && selected.nextElementSibling) {
      (selected.nextElementSibling as HTMLLabelElement).click();
    } else {
      click(".chart-labels label:first-child");
    }
  });
  Mousetrap.bind("C", () => {
    const selected = select(".chart-labels .selected");

    if (selected && selected.previousElementSibling) {
      (selected.previousElementSibling as HTMLLabelElement).click();
    } else {
      click(".chart-labels label:last-child");
    }
  });
});
