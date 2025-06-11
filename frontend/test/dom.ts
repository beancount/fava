import { JSDOM } from "jsdom";

let ran_once = false;

/** Setup jsdom to allow browser-code to run. */
export function setup_jsdom(): void {
  if (!ran_once) {
    const { window } = new JSDOM("", { url: "http://localhost:3000" });
    const window_keys = Object.getOwnPropertyNames(window).filter(
      (key) => !key.startsWith("_") && !(key in global),
    );
    // @ts-expect-error Unexpected in Node
    global.window = window;
    for (const key of window_keys) {
      // @ts-expect-error Unexpected in Node
      // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
      global[key] = window[key];
    }
    ran_once = true;
  }
  window.document.title = "";
  window.document.head.innerHTML = "";
  window.document.body.innerHTML = "";
}
