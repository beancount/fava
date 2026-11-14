import { deepEqual, equal, match, ok, rejects } from "node:assert/strict";
import { type TestContext, test } from "node:test";

import { get as store_get } from "svelte/store";

import ReportLoadError from "../src/reports/ReportLoadError.svelte";
import { type FrontendRoute, Route } from "../src/reports/route.ts";
import type { Router } from "../src/router.ts";
import { raw_page_title } from "../src/sidebar/page-title.ts";
import { setup_jsdom } from "./dom.ts";
import { initialise_ledger_data } from "./helpers.ts";

test.before(initialise_ledger_data);
test.beforeEach(setup_jsdom);

interface Props {
  title: string;
  error: Error;
}

/** A route whose load resolves only once `resolve` is called. */
function deferred_route(report: string): {
  route: Route<Props>;
  signals: AbortSignal[];
  resolve: () => void;
} {
  const signals: AbortSignal[] = [];
  let resolve_load = (): void => {
    throw new Error("load has not been called yet");
  };
  const route = new Route<Props>(
    report,
    ReportLoadError,
    async (_url, signal) => {
      signals.push(signal);
      return new Promise((resolve) => {
        resolve_load = () => {
          resolve({ title: report, error: new Error(report) });
        };
      });
    },
    () => report,
  );
  return {
    route,
    signals,
    resolve: () => {
      resolve_load();
    },
  };
}

/** Wait for the next popstate event. */
async function popstate(): Promise<void> {
  return new Promise((resolve) => {
    window.addEventListener(
      "popstate",
      () => {
        resolve();
      },
      { once: true },
    );
  });
}

/**
 * Create and initialise a router at the given URL.
 *
 * It is destroyed at the end of the test to remove its event listeners.
 */
async function init_router(
  t: TestContext,
  url: string,
  routes: FrontendRoute[],
): Promise<{ router: Router; init: Promise<void> }> {
  // Import dynamically since the module creates a router, which needs a DOM.
  const router_module = await import("../src/router.ts");
  window.history.pushState(null, "", url);
  const router = new router_module.Router();
  t.after(() => {
    router.destroy();
  });
  const init = router.init(routes);
  return { router, init };
}

const article_text = () => document.querySelector("article")?.textContent ?? "";
const base = "http://localhost:3000/long-example/";

test("route render - does not render if aborted during load", async () => {
  const { route, signals, resolve } = deferred_route("test");
  const controller = new AbortController();
  const target = document.createElement("div");

  const rendered = route.render(
    target,
    new URL(window.location.href),
    controller.signal,
  );
  deepEqual(signals, [controller.signal]);
  controller.abort();
  resolve();

  await rejects(rendered, { name: "AbortError" });
  equal(target.innerHTML, "");
});

test("router - navigation aborts the previous report load", async (t) => {
  const start = deferred_route("start");
  const slow = deferred_route("slow");
  const fast = deferred_route("fast");
  const { router, init } = await init_router(t, `${base}start/`, [
    start.route,
    slow.route,
    fast.route,
  ]);
  start.resolve();
  await init;
  equal(store_get(raw_page_title), "start");
  match(article_text(), /Loading start failed/);

  router.navigate(`${base}slow/`);
  router.navigate(`${base}fast/`);
  await new Promise(setImmediate);

  ok(slow.signals[0]);
  ok(slow.signals[0].aborted);
  ok(fast.signals[0]);
  ok(!fast.signals[0].aborted);

  fast.resolve();
  await new Promise(setImmediate);
  equal(store_get(raw_page_title), "fast");
  equal(router.current.href, `${base}fast/`);
  match(article_text(), /Loading fast failed/);

  // Resolving the aborted load later must not render it.
  slow.resolve();
  await new Promise(setImmediate);
  equal(store_get(raw_page_title), "fast");
  equal(router.current.href, `${base}fast/`);
  match(article_text(), /Loading fast failed/);
});

test("router - reload restarts a pending navigation", async (t) => {
  const slow = deferred_route("slow");
  const fast = deferred_route("fast");
  const { router, init } = await init_router(t, `${base}fast/`, [
    slow.route,
    fast.route,
  ]);
  fast.resolve();
  await init;

  router.navigate(`${base}slow/`);
  router.reload();
  await new Promise(setImmediate);
  equal(slow.signals.length, 2);
  equal(slow.signals[0]?.aborted, true);
  slow.resolve();
  await new Promise(setImmediate);

  equal(store_get(raw_page_title), "slow");
  equal(router.current.href, `${base}slow/`);
  equal(window.location.href, `${base}slow/`);
  match(article_text(), /Loading slow failed/);
});

test("router - going back and forward aborts the pending load", async (t) => {
  const slow = deferred_route("slow");
  const fast = deferred_route("fast");
  window.history.pushState(null, "", `${base}fast/`);
  const { router, init } = await init_router(t, `${base}slow/`, [
    slow.route,
    fast.route,
  ]);
  slow.resolve();
  await init;

  const back = popstate();
  window.history.back();
  await back;
  equal(window.location.href, `${base}fast/`);
  ok(fast.signals[0]);
  const forward = popstate();
  window.history.forward();
  await forward;
  equal(window.location.href, `${base}slow/`);
  ok(fast.signals[0].aborted);

  slow.resolve();
  fast.resolve();
  await new Promise(setImmediate);
  equal(store_get(raw_page_title), "slow");
  equal(router.current.href, `${base}slow/`);
  equal(window.location.href, `${base}slow/`);
  match(article_text(), /Loading slow failed/);
});
