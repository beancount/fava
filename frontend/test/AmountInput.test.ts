import { deepEqual, equal, ok } from "node:assert/strict";
import { test } from "node:test";

import { flushSync, mount, unmount } from "svelte";
import { get } from "svelte/store";

import AmountInput from "../src/entry-forms/AmountInput.svelte";
import { ledger_data } from "../src/stores/index.ts";
import { setup_jsdom, user_events } from "./dom.ts";
import { initialise_ledger_data } from "./helpers.ts";

test.before(initialise_ledger_data);
test.beforeEach(setup_jsdom);

/** Mount the `AmountInput` component and return the `<input>`. */
function mount_amount_input(
  t: test.TestContext,
  value = "",
  account?: string,
): HTMLInputElement {
  const component = mount(AmountInput, {
    target: document.body,
    props: { value, account },
  });
  flushSync();

  t.after(async () => {
    await unmount(component);
  });

  const input = document.body.querySelector("input");
  ok(input instanceof HTMLInputElement);
  return input;
}

/** Get the suggestions. */
const suggestion_texts = () =>
  [...document.body.querySelectorAll("li")].map((i) => i.textContent);

test("AmountInput: shows no suggestions for an empty value", (t) => {
  const input = mount_amount_input(t, "");
  user_events.focus(input);

  deepEqual(suggestion_texts(), []);
});

test("AmountInput: shows no suggestions for a whitespace-only value", (t) => {
  const input = mount_amount_input(t, "   ");
  user_events.focus(input);

  deepEqual(suggestion_texts(), []);
});

test("AmountInput: suggests the number together with the known currencies", (t) => {
  const input = mount_amount_input(t, "100");
  user_events.focus(input);

  deepEqual(suggestion_texts(), [
    "100 USD",
    "100 VACHR",
    "100 IRAUSD",
    "100 VBMPX",
    "100 RGAGX",
    "100 GLD",
    "100 VEA",
    "100 VHT",
    "100 ITOT",
    "100 ABC",
    "100 XYZ",
  ]);
});

test("AmountInput: supports negative and decimal numbers", (t) => {
  const input = mount_amount_input(t, "-12.5");
  user_events.focus(input);

  ok(suggestion_texts().includes("-12.5 USD"));
});

test("AmountInput: restricts suggestions to the currencies allowed for the account", (t) => {
  // "Assets:US:BayBook:Vacation" is only opened for VACHR in the example file.
  const input = mount_amount_input(t, "100", "Assets:US:BayBook:Vacation");
  user_events.focus(input);

  deepEqual(suggestion_texts(), ["100 VACHR"]);
});

test("AmountInput: falls back to all currencies for an account without a restriction", (t) => {
  // "Assets:Testing:MultipleCommodities" is opened without currencies.
  const input = mount_amount_input(
    t,
    "100",
    "Assets:Testing:MultipleCommodities",
  );
  user_events.focus(input);

  deepEqual(suggestion_texts(), [
    "100 USD",
    "100 VACHR",
    "100 IRAUSD",
    "100 VBMPX",
    "100 RGAGX",
    "100 GLD",
    "100 VEA",
    "100 VHT",
    "100 ITOT",
    "100 ABC",
    "100 XYZ",
  ]);
});

test("AmountInput: plain blur does not trigger automatic selection", (t) => {
  // On mobile, blur can happen for reasons other than explicit confirmation
  // (e.g. tapping elsewhere) and there is no Escape key to back out of an
  // unwanted selection, so only Tab should trigger it - see below.
  const input = mount_amount_input(t, "100");
  user_events.focus(input);

  user_events.blur(input);
  equal(input.value, "100");
});

test("AmountInput: Tab triggers automatic selection and updates the value", (t) => {
  const input = mount_amount_input(t, "100");
  user_events.focus(input);

  user_events.keydown(input, "Tab");
  user_events.blur(input);
  equal(input.value, "100 USD");
});

test("AmountInput: only uses the leading number, ignoring digits later in the value", (t) => {
  // Use a currency that itself contains digits, so that a regression to
  // naively stripping all non-numeric characters would be caught here.
  const original_ledger_data = get(ledger_data);
  ledger_data.set({ ...original_ledger_data, currencies: ["A123", "USD"] });
  t.after(() => {
    ledger_data.set(original_ledger_data);
  });

  const input = mount_amount_input(t, "");
  user_events.type(input, "100 A1");

  deepEqual(suggestion_texts(), ["100 A123"]);
});
