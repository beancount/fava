import { JSDOM } from "jsdom";

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
  window.document.title = "";
  window.document.head.innerHTML = "";
  window.document.body.innerHTML = "";
}
