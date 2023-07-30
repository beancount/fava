import { tick } from "svelte";
import type { Action } from "svelte/action";

import { log_error } from "./log";

/**
 * Add a tooltip showing the keyboard shortcut over the target element.
 * @param target - The target element to show the tooltip on.
 * @returns A function to remove event handler.
 */
function showTooltip(target: HTMLElement): () => void {
  const tooltip = document.createElement("div");
  const isHidden = target.classList.contains("hidden");
  if (isHidden) {
    target.classList.remove("hidden");
  }
  tooltip.className = "keyboard-tooltip";
  tooltip.textContent = target.getAttribute("data-key") ?? "";
  document.body.appendChild(tooltip);
  const parentCoords = target.getBoundingClientRect();
  // Padded 10px to the left if there is space or centered otherwise
  const left =
    parentCoords.left +
    Math.min((target.offsetWidth - tooltip.offsetWidth) / 2, 10);
  const top =
    parentCoords.top + (target.offsetHeight - tooltip.offsetHeight) / 2;
  tooltip.style.left = `${left}px`;
  tooltip.style.top = `${top + window.scrollY}px`;
  return () => {
    tooltip.remove();
    if (isHidden) {
      target.classList.add("hidden");
    }
  };
}

/**
 * Show all keyboard shortcut tooltips.
 */
function showTooltips(): () => void {
  const removes: (() => void)[] = [];
  document.querySelectorAll("[data-key]").forEach((el) => {
    if (el instanceof HTMLElement) {
      removes.push(showTooltip(el));
    }
  });
  return () => {
    removes.forEach((r) => {
      r();
    });
  };
}

/**
 * Ignore events originating from editable elements.
 * @param element - The element to check.
 * @returns true if the element is one of input/select/textarea or a
 *          contentEditable element.
 */
function isEditableElement(element: EventTarget | null): boolean {
  return (
    element instanceof HTMLElement &&
    (element instanceof HTMLInputElement ||
      element instanceof HTMLSelectElement ||
      element instanceof HTMLTextAreaElement ||
      element.isContentEditable)
  );
}

type UppercaseLetter =
  | "A"
  | "B"
  | "C"
  | "D"
  | "E"
  | "F"
  | "G"
  | "H"
  | "I"
  | "J"
  | "L"
  | "M"
  | "N"
  | "O"
  | "P"
  | "Q"
  | "R"
  | "S"
  | "T"
  | "U"
  | "V"
  | "W"
  | "X"
  | "Y"
  | "Z";
type LowercaseLetter = Lowercase<UppercaseLetter>;
type Letter = UppercaseLetter | LowercaseLetter;
// This type can be extended as needed to support all the desired
// key combinations
type KeyCombo =
  | "?"
  | Letter
  | `${"Control" | "Meta"}+${"d" | "s" | "Enter"}`
  // d,s,t - journal filters; f - filters; g - reports
  | `${"d" | "f" | "g" | "s" | "t"} ${Letter}`;
/** A handler function or an element to click. */
type KeyboardShortcutAction = ((event: KeyboardEvent) => void) | HTMLElement;
const keyboardShortcuts = new Map<string, KeyboardShortcutAction>();
// The last typed character to check for sequences of two keys.
let lastChar = "";

/**
 * Handle a `keydown` event on the document.
 *
 * Dispatch to the relevant handler.
 */
function keydown(event: KeyboardEvent): void {
  if (isEditableElement(event.target)) {
    // ignore events in editable elements.
    return;
  }
  let eventKey = event.key;
  if (event.metaKey) {
    eventKey = `Meta+${eventKey}`;
  }
  if (event.altKey) {
    eventKey = `Alt+${eventKey}`;
  }
  if (event.ctrlKey) {
    eventKey = `Control+${eventKey}`;
  }
  const lastTwoKeys = `${lastChar} ${eventKey}`;
  const handler =
    keyboardShortcuts.get(lastTwoKeys) ?? keyboardShortcuts.get(eventKey);
  if (handler) {
    if (handler instanceof HTMLInputElement) {
      event.preventDefault();
      handler.focus();
    } else if (handler instanceof HTMLElement) {
      event.preventDefault();
      handler.click();
    } else {
      handler(event);
    }
  }
  if (event.key !== "Alt" && event.key !== "Control" && event.key !== "Shift") {
    lastChar = eventKey;
  }
}

document.addEventListener("keydown", keydown);

/** A type to specify a platform-dependent keyboard shortcut. */
export type KeySpec =
  | KeyCombo
  | { key: KeyCombo; mac?: KeyCombo; note?: string };

const isMac =
  // This still seems to be the least bad way to check whether we are running on macOS or iOS
  // eslint-disable-next-line deprecation/deprecation
  navigator.platform.startsWith("Mac") || navigator.platform === "iPhone";

export const modKey = isMac ? "Cmd" : "Ctrl";

/**
 * Get the keyboard key specifier string for the current platform.
 * @param spec - The key spec.
 */
function getKeySpecKey(spec: KeySpec): KeyCombo {
  if (typeof spec === "string") {
    return spec;
  }
  return isMac ? spec.mac ?? spec.key : spec.key;
}

/**
 * Get the keyboard key description.
 * @param spec - The key spec.
 */
function getKeySpecDescription(spec: KeySpec): string {
  if (typeof spec === "string") {
    return spec;
  }
  const key = isMac ? spec.mac ?? spec.key : spec.key;
  return spec.note ? `${key} - ${spec.note}` : key;
}

/**
 * Bind an event handler to a key.
 * @param spec - The key to bind.
 * @param handler - The callback to run on key press.
 * @returns A function to unbind the keyboard handler.
 */
function bindKey(spec: KeySpec, handler: KeyboardShortcutAction): () => void {
  const key = getKeySpecKey(spec);
  const sequence = key.split(" ");
  if (sequence.length > 2) {
    // eslint-disable-next-line no-console
    console.error("Only key sequences of length <=2 are supported: ", key);
  }
  if (keyboardShortcuts.has(key)) {
    // eslint-disable-next-line no-console
    console.warn("Duplicate keyboard shortcut: ", key, handler);
  }
  keyboardShortcuts.set(key, handler);
  return () => {
    keyboardShortcuts.delete(key);
  };
}

/**
 * A svelte action to attach a global keyboard shortcut.
 *
 * This will attach a listener for the given key (or key sequence of length 2).
 * This listener will focus the given node if it is an <input> element and
 * trigger a click on it otherwise.
 */
export const keyboardShortcut: Action<HTMLElement, KeySpec | undefined> = (
  node,
  spec,
) => {
  const setup = (s?: KeySpec) => {
    if (s) {
      node.setAttribute("data-key", getKeySpecDescription(s));
      return bindKey(s, node);
    }
    node.removeAttribute("data-key");
    return () => {};
  };
  let unbind = setup(spec);

  return {
    destroy: unbind,
    update(new_spec) {
      unbind();
      // Await tick so that key bindings that might have been removed from other
      // elements in the same render are gone.
      tick()
        .then(() => {
          unbind = setup(new_spec);
        })
        .catch(log_error);
    },
  };
};

/**
 * Register the keys to show/hide the tooltips
 */
export function initGlobalKeyboardShortcuts(): void {
  bindKey("?", () => {
    const hide = showTooltips();
    const once = () => {
      hide();
      document.removeEventListener("mousedown", once);
      document.removeEventListener("keydown", once);
    };
    document.addEventListener("mousedown", once);
    document.addEventListener("keydown", once);
  });
}
