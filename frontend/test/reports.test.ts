import { equal } from "node:assert/strict";
import { test } from "node:test";

import { mount, tick, unmount } from "svelte";

import { Document } from "../src/entries/index.ts";
import { array } from "../src/lib/validation.ts";
import { setup_jsdom } from "./dom.ts";
import { initialiseLedgerData, loadJSONSnapshot } from "./helpers.ts";

test.before(initialiseLedgerData);
test.beforeEach(setup_jsdom);

test("render documents report", async () => {
  const documents_component = (
    await import("../src/reports/documents/Documents.svelte")
  ).default;

  const data = await loadJSONSnapshot("test_json_api-test_api-documents.json");
  const documents = array(Document.validator)(data).unwrap();

  const component = mount(documents_component, {
    target: document.body,
    props: { documents },
  });

  await tick();

  equal(document.querySelectorAll("table tbody tr").length, documents.length);

  unmount(component);
});
