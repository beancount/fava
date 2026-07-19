import { equal, ok } from "node:assert/strict";
import { beforeEach, test } from "node:test";

import { flushSync, mount } from "svelte";

import { Balance } from "../src/entries/index.ts";
import BalanceForm from "../src/entry-forms/Balance.svelte";
import { setup_jsdom } from "./dom.ts";
import { initialiseLedgerData } from "./helpers.ts";

test.before(initialiseLedgerData);
beforeEach(setup_jsdom);

test("Balance form uses a decimal keyboard hint for the amount input", () => {
  mount(BalanceForm, {
    target: document.body,
    props: {
      entry: Balance.empty("2026-05-27"),
    },
  });
  flushSync();

  const input = document.body.querySelector('input[placeholder="Number"]');
  ok(input instanceof HTMLInputElement);
  equal(input.type, "text");
  equal(input.inputMode, "decimal");
  equal(input.pattern, "-?[0-9.,]*");
});
