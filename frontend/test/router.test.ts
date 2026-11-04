import { deepEqual, equal, ok } from "node:assert/strict";
import { test } from "node:test";
import { setImmediate } from "node:timers/promises";

import { get } from "svelte/store";

import { object, string } from "../src/lib/validation.ts";
import { current_url } from "../src/stores/url.ts";
import { setup_jsdom } from "./dom.ts";
import { initialise_ledger_data } from "./helpers.ts";

test("router restores history scroll positions after rendering", async (t) => {
  setup_jsdom();
  await initialise_ledger_data();
  const previous_url = get(current_url);
  const router_module = await import("../src/router.ts");
  const routes_module = await import("../src/reports/route.ts");
  t.after(() => {
    current_url.set(previous_url);
  });
  const article = document.querySelector("article");
  ok(article);
  const base = "http://localhost:3000/long-example/";
  window.history.replaceState(
    { extension: "preserved" },
    "",
    `${base}balance_sheet/`,
  );
  const router = new router_module.Router();

  // JSDOM has no layout. Simulate the short account report clamping scroll
  // offsets so restoring before the taller balance sheet renders would fail.
  let height = 2000;
  Object.defineProperty(article, "scroll", {
    configurable: true,
    value: (left: number, top: number) => {
      article.scrollLeft = left;
      article.scrollTop = Math.min(top, height);
    },
  });
  t.mock.method(window, "scroll", (left: number, top: number) => {
    window.scrollX = left;
    window.scrollY = Math.min(top, height);
  });
  const window_listeners = t.mock.method(window, "addEventListener");
  const document_listeners = t.mock.method(document, "addEventListener");
  t.after(() => {
    for (const { arguments: args } of window_listeners.mock.calls) {
      window.removeEventListener(...args);
    }
    for (const { arguments: args } of document_listeners.mock.calls) {
      document.removeEventListener(...args);
    }
  });

  let renders = 0;
  const routes = ["balance_sheet", "account"].map((report) => ({
    report,
    async render(
      target: HTMLElement,
      url: URL,
      previous?: InstanceType<typeof routes_module.RenderedReport>,
      before_render?: () => void,
    ) {
      await Promise.resolve();
      previous?.destroy();
      before_render?.();
      height = report === "balance_sheet" ? 2000 : 300;
      target.textContent = report;
      renders += 1;
      return new routes_module.RenderedReport(this, url, report, () => {
        target.textContent = "";
      });
    },
  }));
  await router.init(routes);
  equal(window.history.scrollRestoration, "manual");
  equal(
    object({ extension: string })(window.history.state).unwrap().extension,
    "preserved",
  );

  const position = () => [
    article.scrollLeft,
    article.scrollTop,
    window.scrollX,
    window.scrollY,
  ];
  const traverse = async (direction: "back" | "forward") => {
    const popped = new Promise<void>((resolve) => {
      window.addEventListener(
        "popstate",
        () => {
          resolve();
        },
        { once: true },
      );
    });
    window.history[direction]();
    await popped;
    await setImmediate();
  };

  await t.test(
    "back and forward restore desktop and mobile scroll",
    async () => {
      article.scroll(30, 900);
      window.scroll(10, 700);
      router.navigate(`${base}account/Assets/`);
      await setImmediate();
      deepEqual(position(), [0, 0, 0, 0]);
      article.scroll(20, 200);
      window.scroll(5, 150);
      await traverse("back");
      deepEqual(position(), [30, 900, 10, 700]);
      await traverse("forward");
      deepEqual(position(), [20, 200, 5, 150]);
    },
  );

  await t.test(
    "revisiting the same URL creates an independent position",
    async () => {
      router.navigate(`${base}balance_sheet/`);
      await setImmediate();
      deepEqual(position(), [0, 0, 0, 0]);
      article.scroll(0, 1200);
      window.scroll(0, 1000);
      await traverse("back");
      deepEqual(position(), [20, 200, 5, 150]);
      await traverse("back");
      deepEqual(position(), [30, 900, 10, 700]);
      await traverse("forward");
      await traverse("forward");
      deepEqual(position(), [0, 1200, 0, 1000]);
    },
  );

  await t.test(
    "filter changes restore the previous report position",
    async () => {
      router.set_search_param("time", "2026");
      await setImmediate();
      deepEqual(position(), [0, 0, 0, 0]);
      article.scroll(0, 600);
      await traverse("back");
      deepEqual(position(), [0, 1200, 0, 1000]);
      await traverse("forward");
      deepEqual(position(), [0, 600, 0, 0]);
    },
  );

  await t.test(
    "view-only changes and overlays do not reload reports",
    async () => {
      const previous_renders = renders;
      router.set_search_param("charts", "false");
      await setImmediate();
      article.scroll(0, 400);
      router.navigate(`${router.current.href}#overlay`, false);
      article.scroll(0, 200);
      await traverse("back");
      deepEqual(position(), [0, 400, 0, 0]);
      await traverse("back");
      deepEqual(position(), [0, 600, 0, 0]);
      equal(renders, previous_renders);
    },
  );

  await t.test("reloading the report retains its position", async () => {
    router.reload();
    await setImmediate();
    deepEqual(position(), [0, 600, 0, 0]);
  });

  await t.test(
    "native hash links retain the underlying report position",
    async () => {
      const previous_renders = renders;
      const popped = new Promise<void>((resolve) => {
        window.addEventListener(
          "popstate",
          () => {
            resolve();
          },
          { once: true },
        );
      });
      window.location.hash = "context-entry";
      await popped;
      await setImmediate();
      article.scroll(0, 200);
      await traverse("back");
      deepEqual(position(), [0, 600, 0, 0]);
      await traverse("forward");
      deepEqual(position(), [0, 200, 0, 0]);
      equal(renders, previous_renders);
    },
  );
});
