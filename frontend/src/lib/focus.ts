const FOCUSABLE_ELEMENTS = [
  "a[href]",
  'input:not([disabled]):not([type="hidden"]):not([aria-hidden])',
  "select:not([disabled]):not([aria-hidden])",
  "textarea:not([disabled]):not([aria-hidden])",
  "button:not([disabled]):not([aria-hidden])",
  "object",
  "[contenteditable]",
].join(", ");

export function getFocusableElements(el: Element): Element[] {
  return [...el.querySelectorAll(FOCUSABLE_ELEMENTS)];
}

/**
 * Focus a node (if possible).
 * @returns whether focusing succeeded.
 */
export function attemptFocus(el: Node): boolean {
  try {
    // @ts-expect-error We are attempting to focus any kind of element here.
    // eslint-disable-next-line @typescript-eslint/no-unsafe-call
    el.focus();
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (e) {
    // pass
  }
  return document.activeElement === el;
}
