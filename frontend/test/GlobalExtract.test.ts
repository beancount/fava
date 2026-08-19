/* eslint-disable @typescript-eslint/naming-convention */
import { equal, ok } from "node:assert/strict";
import { before, beforeEach, test } from "node:test";

import { setup_jsdom } from "./dom.ts";

// Setup JSDOM immediately before any other ESM modules are loaded
setup_jsdom();
// Router constructor expects an <article> element to be present in the document
const article = document.createElement("article");
document.body.appendChild(article);

// Now we can safely import other modules that depend on `window` being defined at top-level
const { flushSync, mount } = await import("svelte");
const { current_url } = await import("../src/stores/url.ts");
const { default: GlobalExtract } = await import(
  "../src/modals/GlobalExtract.svelte"
);
const { initialiseLedgerData } = await import("./helpers.ts");

before(initialiseLedgerData);
beforeEach(() => {
  setup_jsdom();
  // Ensure the article element is recreated for any router operations during tests
  const article = document.createElement("article");
  document.body.appendChild(article);
});

test("GlobalExtract: mounts and does nothing if hash is empty", () => {
  current_url.set(new URL("http://localhost:3000"));

  mount(GlobalExtract, {
    target: document.body,
  });
  flushSync();

  const modal = document.body.querySelector("form");
  ok(!modal);
});

test("GlobalExtract: automatically closes (clears hash) if hash is malformed (missing parameters)", () => {
  current_url.set(
    new URL("http://localhost:3000/#extract?filename=only_filename"),
  );

  mount(GlobalExtract, {
    target: document.body,
  });
  flushSync();

  equal(window.location.hash, "");
});

test("GlobalExtract: fetches and displays extract modal on valid hash", async (t) => {
  current_url.set(
    new URL(
      "http://localhost:3000/#extract?filename=file.csv&importer=my-importer",
    ),
  );

  const mock_entry = {
    t: "Balance",
    meta: { filename: "/home/test/test.beancount", lineno: 1 },
    date: "2022-12-12",
    entry_hash: "ENTRY_HASH",
    account: "Expenses:Food",
    amount: { number: "10", currency: "USD" },
  };

  t.mock.method(globalThis, "fetch", (urlStr: string | URL) => {
    const url = new URL(urlStr);
    if (url.pathname.endsWith("/api/extract")) {
      return new Response(JSON.stringify({ data: [mock_entry] }));
    }
    return new Response(JSON.stringify({ data: [] }));
  });

  mount(GlobalExtract, {
    target: document.body,
  });

  flushSync();
  await new Promise((resolve) => setTimeout(resolve, 10));
  flushSync();

  const modalHeader = document.body.querySelector("h3");
  ok(modalHeader);
  equal(modalHeader.textContent, "Import");
});

test("GlobalExtract: closes and warns if API returns empty list", async (t) => {
  current_url.set(
    new URL(
      "http://localhost:3000/#extract?filename=file.csv&importer=my-importer",
    ),
  );

  t.mock.method(globalThis, "fetch", (urlStr: string | URL) => {
    const url = new URL(urlStr);
    if (url.pathname.endsWith("/api/extract")) {
      return new Response(JSON.stringify({ data: [] }));
    }
    return new Response(JSON.stringify({ data: [] }));
  });

  mount(GlobalExtract, {
    target: document.body,
  });

  flushSync();
  await new Promise((resolve) => setTimeout(resolve, 10));
  flushSync();

  equal(window.location.hash, "");

  const notification = document.body.querySelector(".notifications li.warning");
  ok(notification);
  equal(notification.textContent, "No entries to import from this file.");
});

test("GlobalExtract: saves non-duplicate entries and closes on save", async (t) => {
  current_url.set(
    new URL(
      "http://localhost:3000/#extract?filename=file.csv&importer=my-importer",
    ),
  );

  const mock_entry = {
    t: "Balance",
    meta: { filename: "/home/test/test.beancount", lineno: 1 },
    date: "2022-12-12",
    entry_hash: "ENTRY_HASH",
    account: "Expenses:Food",
    amount: { number: "10", currency: "USD" },
  };

  interface MockSavedEntry {
    account: string;
  }
  let savedEntries: MockSavedEntry[] = [];
  t.mock.method(
    globalThis,
    "fetch",
    (urlStr: string | URL, init?: RequestInit) => {
      const url = new URL(urlStr);
      if (url.pathname.endsWith("/api/extract")) {
        return new Response(JSON.stringify({ data: [mock_entry] }));
      }
      if (url.pathname.endsWith("/api/add_entries")) {
        if (init?.body != null) {
          const body = JSON.parse(init.body as string) as {
            entries: MockSavedEntry[];
          };
          savedEntries = body.entries;
        }
        return new Response(JSON.stringify({ data: "Success" }));
      }
      return new Response(JSON.stringify({ data: [] }));
    },
  );

  mount(GlobalExtract, {
    target: document.body,
  });

  flushSync();
  await new Promise((resolve) => setTimeout(resolve, 10));
  flushSync();

  const form = document.body.querySelector("form");
  ok(form instanceof HTMLFormElement);
  form.dispatchEvent(
    new window.Event("submit", { bubbles: true, cancelable: true }),
  );

  flushSync();
  await new Promise((resolve) => setTimeout(resolve, 10));
  flushSync();

  equal(window.location.hash, "");

  equal(savedEntries.length, 1);
  const firstEntry = savedEntries[0];
  ok(firstEntry);
  equal(firstEntry.account, "Expenses:Food");
});
