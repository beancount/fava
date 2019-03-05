import Mousetrap from "mousetrap";

import { $, $$ } from "./helpers";
import e from "./events";
import { closeOverlay } from "./stores";

function click(selector) {
  const element = $(selector);
  if (element) {
    element.click();
  }
}

e.on("page-loaded", () => {
  $$("[data-key]").forEach(element => {
    const key = element.getAttribute("data-key");
    if (key !== undefined) {
      Mousetrap.bind(
        key,
        () => {
          const tag = element.tagName;
          if (tag === "BUTTON" || tag === "A") {
            element.click();
          } else if (tag === "INPUT") {
            element.focus();
          }
        },
        "keyup"
      );
    }
  });
});

// Add a tooltip showing the keyboard shortcut over the target element.
function showTooltip(target) {
  const tooltip = document.createElement("div");
  tooltip.className = "keyboard-tooltip";
  tooltip.innerHTML = target.getAttribute("data-key");
  document.body.appendChild(tooltip);
  const parentCoords = target.getBoundingClientRect();
  // Padded 10px to the left if there is space or centered otherwise
  const left =
    parentCoords.left +
    Math.min((target.offsetWidth - tooltip.offsetWidth) / 2, 10);
  const top =
    parentCoords.top + (target.offsetHeight - tooltip.offsetHeight) / 2;
  tooltip.style.left = `${parseInt(left, 10)}px`;
  tooltip.style.top = `${parseInt(top, 10) + window.pageYOffset}px`;
}

// Show all keyboard shortcut tooltips.
function showTooltips() {
  $("#reload-page").classList.remove("hidden");
  $$("[data-key]").forEach(el => {
    showTooltip(el);
  });
}

// Remove all keyboard shortcut tooltips.
function removeTooltips() {
  $("#reload-page").classList.add("hidden");
  $$(".keyboard-tooltip").forEach(tooltip => {
    tooltip.remove();
  });
}

e.on("page-init", () => {
  Mousetrap.bind("?", () => {
    removeTooltips();
    showTooltips();
    $.once(document, "mousedown", () => {
      removeTooltips();
    });
  });

  Mousetrap.bind("esc", () => {
    closeOverlay();
    removeTooltips();
  });

  // Charts
  Mousetrap.bind("c", () => {
    const selected = $("#chart-labels .selected");

    if (selected && selected.nextElementSibling) {
      selected.nextElementSibling.click();
    } else {
      click("#chart-labels label:first-child");
    }
  });
  Mousetrap.bind("C", () => {
    const selected = $("#chart-labels .selected");

    if (selected && selected.previousElementSibling) {
      selected.previousElementSibling.click();
    } else {
      click("#chart-labels label:last-child");
    }
  });
});
