import { deepEqual, equal, ok } from "node:assert/strict";
import { test } from "node:test";

import { flushSync, mount, unmount } from "svelte";
import { fromStore, writable } from "svelte/store";

import { EntryMetadata } from "../src/entries/metadata.ts";
import EntryMetadataForm from "../src/entry-forms/EntryMetadata.svelte";
import { setup_jsdom, user_events } from "./dom.ts";

test.beforeEach(setup_jsdom);

/** Mount the metadata rows in a form and expose their current save payload. */
function mount_metadata(t: test.TestContext, initial: EntryMetadata) {
  const metadata = fromStore(writable(initial));
  const form = document.createElement("form");
  document.body.appendChild(form);
  const component = mount(EntryMetadataForm, {
    target: form,
    props: {
      get meta() {
        return metadata.current;
      },
      set meta(value: EntryMetadata) {
        metadata.current = value;
      },
    },
  });
  flushSync();
  t.after(async () => {
    await unmount(component);
  });
  return {
    form,
    payload: (): unknown => JSON.parse(JSON.stringify(metadata.current)),
  };
}

function change_value(
  field: HTMLInputElement | HTMLSelectElement,
  value: string,
) {
  field.value = value;
  field.dispatchEvent(new window.Event("change", { bubbles: true }));
  flushSync();
}

test("metadata form: a new number keeps its precision and can be changed to literal text", (t) => {
  const { form, payload } = mount_metadata(t, new EntryMetadata().add());
  const key = form.querySelector("input.key");
  ok(key instanceof HTMLInputElement);
  change_value(key, "reference");
  const kind = form.querySelector("select");
  const value = form.querySelector("input.value");
  ok(kind instanceof HTMLSelectElement);
  ok(value instanceof HTMLInputElement);

  equal(kind.value, "text");
  change_value(kind, "number");
  equal(form.checkValidity(), false);
  deepEqual(payload(), { reference: "" });
  const exact = "0.1234567891011121314151617";
  user_events.type(value, exact);
  equal(form.checkValidity(), true);
  deepEqual(payload(), { reference: { number: exact } });

  change_value(kind, "text");
  equal(value.value, exact);
  user_events.type(value, "10.10");
  deepEqual(payload(), { reference: "10.10" });
  user_events.type(value, "00123");
  deepEqual(payload(), { reference: "00123" });
  change_value(kind, "number");
  deepEqual(payload(), { reference: { number: "00123" } });
});

test("metadata form: invalid numbers block submission and keep the last valid value", (t) => {
  const { form, payload } = mount_metadata(
    t,
    EntryMetadata.validator({ number: { number: "10.10" } }).unwrap(),
  );
  const kind = form.querySelector("select");
  const value = form.querySelector("input.value");
  ok(kind instanceof HTMLSelectElement);
  ok(value instanceof HTMLInputElement);
  equal(kind.value, "number");

  for (const invalid of ["", "1.2.3", "TRUE"]) {
    user_events.type(value, invalid);
    equal(form.checkValidity(), false);
    deepEqual(payload(), { number: { number: "10.10" } });
  }

  change_value(kind, "text");
  equal(form.checkValidity(), true);
  deepEqual(payload(), { number: "TRUE" });

  change_value(kind, "auto");
  deepEqual(payload(), { number: true });
  user_events.type(value, "1");
  user_events.type(value, "10.10 USD");
  change_value(value, "10.10 USD");
  deepEqual(payload(), { number: { number: "10.10", currency: "USD" } });
});
