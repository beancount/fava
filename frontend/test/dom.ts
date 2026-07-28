import { JSDOM } from "jsdom";
import { flushSync } from "svelte";

let ran_once = false;

/** Setup jsdom to allow browser-code to run. */
export function setup_jsdom(): void {
  if (!ran_once) {
    const { window } = new JSDOM("", { url: "http://localhost:3000" });
    const window_keys = Object.getOwnPropertyNames(window).filter(
      (key) => !key.startsWith("_") && !(key in globalThis),
    );
    // @ts-expect-error Unexpected in Node
    globalThis.window = window;
    for (const key of window_keys) {
      // @ts-expect-error Unexpected in Node
      // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
      globalThis[key] = window[key];
    }
    globalThis.StorageEvent = window.StorageEvent;
    globalThis.localStorage = window.localStorage;
    globalThis.sessionStorage = window.sessionStorage;
    ran_once = true;
  }
  document.title = "";
  document.head.innerHTML = "";
  document.body.innerHTML = "";

  const article = document.createElement("article");
  document.body.appendChild(article);

  const script = document.createElement("script");
  script.type = "application/json";
  script.id = "translations";
  script.textContent = "{}";
  document.body.appendChild(script);
}

/** Trigger some common browser events. */
export const user_events = {
  /** Blur the element. */
  blur(el: HTMLElement): void {
    el.dispatchEvent(new window.Event("blur"));
    flushSync();
  },
  /** Click the element. */
  click(el: HTMLElement): void {
    el.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    flushSync();
  },
  /** Focus the element. */
  focus(input: HTMLInputElement): void {
    input.dispatchEvent(new FocusEvent("focus"));
    flushSync();
  },
  /** Trigger a keydown event. */
  keydown(
    input: HTMLInputElement,
    key: string,
    eventInitDict: KeyboardEventInit = {},
  ): boolean {
    const event = new KeyboardEvent("keydown", {
      key,
      bubbles: true,
      cancelable: true,
      ...eventInitDict,
    });
    const not_prevented = input.dispatchEvent(event);
    flushSync();
    return not_prevented;
  },
  /** Trigger a mousedown event. */
  mousedown(el: HTMLElement, eventInitDict: MouseEventInit = {}): void {
    el.dispatchEvent(
      new MouseEvent("mousedown", { bubbles: true, ...eventInitDict }),
    );
    flushSync();
  },
  /** Type a value into the input, as a user would. */
  type(input: HTMLInputElement, value: string): void {
    input.value = value;
    input.dispatchEvent(new InputEvent("input", { bubbles: true }));
    flushSync();
  },
};
