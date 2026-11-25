import { equal, ok } from "node:assert/strict";
import { test } from "node:test";

import { flushSync, mount, unmount } from "svelte";
import { fromStore, get, writable } from "svelte/store";

import { RawAmount } from "../src/entries/amount.ts";
import { Balance as BalanceEntry } from "../src/entries/index.ts";
import Balance from "../src/entry-forms/Balance.svelte";
import { accounts } from "../src/stores/index.ts";
import { setup_jsdom, user_events } from "./dom.ts";
import { initialise_ledger_data } from "./helpers.ts";

test.before(initialise_ledger_data);
test.beforeEach(setup_jsdom);

interface MountedBalance {
  input: HTMLInputElement;
  get_entry: () => BalanceEntry;
  set_entry: (next: BalanceEntry) => void;
}

/** Mount the `Balance` component with a reactive `bind:entry` harness. */
function mount_balance(
  t: test.TestContext,
  initial_entry = BalanceEntry.empty("2025-01-01"),
  target: HTMLElement = document.body,
): MountedBalance {
  const entry_store = writable(initial_entry);
  const entry_reactive = fromStore(entry_store);
  const component = mount(Balance, {
    target,
    props: {
      get entry(): BalanceEntry {
        return entry_reactive.current;
      },
      set entry(value: BalanceEntry) {
        entry_reactive.current = value;
      },
    },
  });
  flushSync();

  t.after(async () => {
    await unmount(component);
  });

  const input = target.querySelector('input[placeholder="Number"]');
  ok(input instanceof HTMLInputElement);

  const get_entry = (): BalanceEntry => get(entry_store);
  const set_entry = (next: BalanceEntry): void => {
    entry_store.set(next);
    flushSync();
  };

  return { input, get_entry, set_entry };
}

test("Balance: evaluates arithmetic expression while keeping raw input text", (t) => {
  const { input, get_entry } = mount_balance(t);

  user_events.type(input, "(10 + 0.25)");
  equal(input.value, "(10 + 0.25)");
  equal(get_entry().amount.number, "10.25");
  equal(input.validity.valid, true);
  equal(input.validationMessage, "");
});

test("Balance: marks incomplete or invalid expressions invalid without overwriting input", (t) => {
  const { input, get_entry } = mount_balance(t);

  user_events.type(input, "10.25");
  equal(get_entry().amount.number, "10.25");
  equal(input.validity.valid, true);

  user_events.type(input, "(10 +");
  equal(input.value, "(10 +");
  equal(get_entry().amount.number, "10.25");
  equal(input.validity.valid, false);
  ok(input.validationMessage.length > 0);

  user_events.type(input, "(10 + 0.25)");
  equal(input.value, "(10 + 0.25)");
  equal(get_entry().amount.number, "10.25");
  equal(input.validity.valid, true);
  equal(input.validationMessage, "");
});

test("Balance: marks whitespace-only input invalid without overwriting model", (t) => {
  const { input, get_entry } = mount_balance(t);

  user_events.type(input, "10.25");
  equal(get_entry().amount.number, "10.25");

  user_events.type(input, "   ");
  equal(input.value, "   ");
  equal(get_entry().amount.number, "10.25");
  equal(input.validity.customError, true);
  equal(input.validity.valid, false);
  ok(input.validationMessage.length > 0);
});

test("Balance: clearing input removes custom validity and relies on required", (t) => {
  const { input, get_entry } = mount_balance(t);

  user_events.type(input, "(10 +");
  equal(input.validity.customError, true);

  user_events.type(input, "");
  equal(input.value, "");
  equal(get_entry().amount.number, "");
  equal(input.validity.customError, false);
  equal(input.validity.valueMissing, true);
  equal(input.validity.valid, false);
});

test("Balance: preserves plain decimal trailing zeros", (t) => {
  const { input, get_entry } = mount_balance(t);

  user_events.type(input, "10.00");
  equal(input.value, "10.00");
  equal(get_entry().amount.number, "10.00");
  equal(input.validity.valid, true);
});

test("Balance: updates input display when parent resets or updates entry", (t) => {
  const { input, get_entry, set_entry } = mount_balance(t);

  user_events.type(input, "(10 + 0.25)");
  equal(input.value, "(10 + 0.25)");
  equal(get_entry().amount.number, "10.25");

  set_entry(BalanceEntry.empty("2025-01-02"));
  equal(input.value, "");
  equal(input.validity.customError, false);
  equal(input.validity.valueMissing, true);

  set_entry(
    new BalanceEntry(
      get_entry().meta,
      "2025-01-03",
      "",
      "Assets:Cash",
      new RawAmount("42.50", "USD"),
    ),
  );
  equal(input.value, "42.50");
  equal(input.validity.valid, true);
});

test("Balance: resets invalid input when parent replaces an initially empty entry", (t) => {
  const { input, get_entry, set_entry } = mount_balance(t);

  user_events.type(input, "(10 +");
  equal(input.value, "(10 +");
  equal(get_entry().amount.number, "");
  equal(input.validity.customError, true);

  const currency_input = document.body.querySelector(
    'input[placeholder="Currency"]',
  );
  ok(currency_input instanceof HTMLInputElement);
  user_events.type(currency_input, "USD");
  equal(input.value, "(10 +");
  equal(get_entry().amount.currency, "USD");

  set_entry(BalanceEntry.empty("2025-01-02"));
  equal(input.value, "");
  equal(input.validity.customError, false);
  equal(input.validity.valueMissing, true);
});

test("Balance: integrates with native HTML form validation and submission", (t) => {
  const form = document.createElement("form");
  const onsubmit = t.mock.fn((event: SubmitEvent) => {
    event.preventDefault();
  });
  form.addEventListener("submit", onsubmit);
  document.body.appendChild(form);

  const account = get(accounts)[0];
  ok(account !== undefined);
  const initial_entry = new BalanceEntry(
    BalanceEntry.empty("2025-01-01").meta,
    "2025-01-01",
    "",
    account,
    new RawAmount("", "USD"),
  );
  const { input, get_entry } = mount_balance(t, initial_entry, form);

  user_events.type(input, "(10 +");
  equal(form.checkValidity(), false);
  form.requestSubmit();
  equal(onsubmit.mock.callCount(), 0);

  user_events.type(input, "   ");
  equal(form.checkValidity(), false);
  form.requestSubmit();
  equal(onsubmit.mock.callCount(), 0);

  user_events.type(input, "(10 + 0.25)");
  equal(form.checkValidity(), true);
  form.requestSubmit();
  equal(onsubmit.mock.callCount(), 1);
  equal(get_entry().amount.number, "10.25");
});
