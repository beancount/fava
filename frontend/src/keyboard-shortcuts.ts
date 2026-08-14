import type { Attachment } from "svelte/attachments";

/**
 * Ignore events originating from editable elements.
 * @param element - The element to check.
 * @returns true if the element is one of input/select/textarea or a
 *          contentEditable element.
 */
function is_editable_element(element: EventTarget | null): boolean {
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
 * Normalise an event key, including modifiers, e.g. `Control+Enter`
 */
export function normalise_key(event: KeyboardEvent): string {
  let key = event.key;
  if (event.metaKey) {
    key = `Meta+${key}`;
  }
  if (event.altKey) {
    key = `Alt+${key}`;
  }
  if (event.ctrlKey) {
    key = `Control+${key}`;
  }
  return key;
}

/**
 * Handle a `keydown` event on the document.
 *
 * Dispatch to the relevant handler.
 */
function keydown(event: KeyboardEvent): void {
  if (is_editable_element(event.target)) {
    // ignore events in editable elements.
    return;
  }
  const eventKey = normalise_key(event);
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

/** A type to specify a platform-dependent keyboard shortcut. */
export type KeySpec =
  | KeyCombo
  | { key: KeyCombo; mac?: KeyCombo; note?: string };

const isMac =
  // This still seems to be the least bad way to check whether we are running on macOS or iOS

  navigator.platform.startsWith("Mac") || navigator.platform === "iPhone";

export const modKey = isMac ? "Cmd" : "Ctrl";

/**
 * Get the keyboard key specifier string for the current platform.
 * @param spec - The key spec.
 */
function get_key_spec_key(spec: KeySpec): KeyCombo {
  if (typeof spec === "string") {
    return spec;
  }
  return isMac ? (spec.mac ?? spec.key) : spec.key;
}

/**
 * Get the keyboard key description.
 * @param spec - The key spec.
 */
function get_key_spec_description(spec: KeySpec): string {
  if (typeof spec === "string") {
    return spec;
  }
  const key = isMac ? (spec.mac ?? spec.key) : spec.key;
  return spec.note != null ? `${key} - ${spec.note}` : key;
}

/**
 * Bind an event handler to a key.
 * @param spec - The key to bind.
 * @param handler - The callback to run on key press.
 * @returns A function to unbind the keyboard handler.
 */
function bind_key(spec: KeySpec, handler: KeyboardShortcutAction): () => void {
  const key = get_key_spec_key(spec);
  const sequence = key.split(" ");
  if (sequence.length > 2) {
    console.error("Only key sequences of length <=2 are supported: ", key);
  }
  if (keyboardShortcuts.has(key)) {
    console.warn("Duplicate keyboard shortcut: ", key, handler);
  }
  keyboardShortcuts.set(key, handler);
  return () => {
    keyboardShortcuts.delete(key);
  };
}

/**
 * A svelte attachment to attach a global keyboard shortcut.
 *
 * This will attach a listener for the given key (or key sequence of length 2).
 * This listener will focus the given node if it is an <input> element and
 * trigger a click on it otherwise.
 */
export const keyboardShortcut = (
  spec?: KeySpec,
): Attachment<HTMLElement> | null => {
  if (spec == null) {
    return null;
  }
  return (node) => {
    node.setAttribute("data-key", get_key_spec_description(spec));
    const unbind = bind_key(spec, node);
    return () => {
      unbind();
      node.removeAttribute("data-key");
    };
  };
};

interface Tooltip {
  target: HTMLElement;
  tooltip: HTMLDivElement;
  target_was_hidden: boolean;
}

/**
 * Show keyboard shortcut tooltips.
 */
export function show_keyboard_shortcuts(): void {
  const controller = new AbortController();
  const { signal } = controller;

  const tooltips: Tooltip[] = [];

  document.querySelectorAll("[data-key]").forEach((target) => {
    const key = target.getAttribute("data-key");
    if (target instanceof HTMLElement && key != null) {
      const target_was_hidden = target.hidden !== false;
      if (target_was_hidden) {
        target.hidden = false;
      }
      const tooltip = document.createElement("div");
      tooltip.className = "keyboard-tooltip";
      tooltip.textContent = key;
      document.body.appendChild(tooltip);

      tooltips.push({ target, tooltip, target_was_hidden });
    }
  });

  tooltips
    .map(({ target, tooltip }) => {
      const rect = target.getBoundingClientRect();
      const left =
        rect.left +
        Math.min((target.offsetWidth - tooltip.offsetWidth) / 2, 10) +
        window.scrollX;
      const top =
        rect.top +
        (target.offsetHeight - tooltip.offsetHeight) / 2 +
        window.scrollY;
      return { left, top, tooltip };
    })
    .forEach(({ left, top, tooltip }) => {
      tooltip.style.left = `${left.toString()}px`;
      tooltip.style.top = `${top.toString()}px`;
    });

  const clear_tooltips = () => {
    tooltips.forEach(({ tooltip, target, target_was_hidden }) => {
      if (target_was_hidden) {
        target.hidden = true;
      }
      tooltip.remove();
    });
    controller.abort();
  };

  document.addEventListener("mousedown", clear_tooltips, { signal });
  document.addEventListener("keydown", clear_tooltips, { signal });
  document.addEventListener("scroll", clear_tooltips, {
    capture: true,
    signal,
  });
  window.addEventListener("resize", clear_tooltips, { signal });
}

/**
 * Register the keys to show/hide the tooltips and register the global keydown handler.
 */
export function init_global_keyboard_shortcuts(): void {
  document.addEventListener("keydown", keydown);
}
