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
  return (): void => {
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
  return (): void => {
    removes.forEach((r) => r());
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
export type KeySpec = string | { key: string; mac: string };

const currentPlatform: "mac" | "key" =
  typeof navigator !== "undefined" && /Mac/.test(navigator.platform)
    ? "mac"
    : "key";

export const modKey = currentPlatform === "mac" ? "Cmd" : "Ctrl";

/**
 * Get the keyboard key specifier string for the current platform.
 * @param keySpec - The key spec.
 */
export function getKeySpecKey(keySpec: KeySpec): string {
  if (typeof keySpec === "string") {
    return keySpec;
  }
  return currentPlatform === "mac" ? keySpec.mac : keySpec.key;
}

/**
 * Bind an event handler to a key.
 * @param key - The key to bind.
 * @param handler - The callback to run on key press.
 * @returns A function to unbind the keyboard handler.
 */
export function bindKey(
  keySpec: KeySpec,
  handler: KeyboardShortcutAction
): () => void {
  const key = getKeySpecKey(keySpec);
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
  return (): void => {
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
export function keyboardShortcut(
  node: HTMLElement,
  key?: string
): { destroy?: () => void } {
  if (!key) {
    return {};
  }
  node.setAttribute("data-key", key);
  const destroy = bindKey(key, node);

  return { destroy };
}

/**
 * Register keyboard shortcuts for all newly added elements with a
 * `data-keyboard-shortcut` attribute.
 */
export function initCurrentKeyboardShortcuts(): void {
  // clean up
  for (const [key, action] of keyboardShortcuts.entries()) {
    if (action instanceof HTMLElement && !document.contains(action)) {
      keyboardShortcuts.delete(key);
    }
  }
  document.querySelectorAll("[data-keyboard-shortcut]").forEach((element) => {
    const key = element.getAttribute("data-keyboard-shortcut");
    if (key && element instanceof HTMLElement) {
      element.removeAttribute("data-keyboard-shortcut");
      element.setAttribute("data-key", key);
      bindKey(key, element);
    }
  });
}

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
