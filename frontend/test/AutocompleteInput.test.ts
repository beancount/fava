import { equal, ok } from "node:assert/strict";
import { beforeEach, test } from "node:test";

import { flushSync, mount } from "svelte";

import AutocompleteInput from "../src/AutocompleteInput.svelte";
import { setup_jsdom } from "./dom.ts";

beforeEach(setup_jsdom);

test("AutocompleteInput: renders no suggestions if none match", () => {
  mount(AutocompleteInput, {
    target: document.body,
    props: {
      value: "nomatch",
      placeholder: "test placeholder",
      suggestions: ["apple", "banana", "cherry"],
    },
  });
  flushSync();
  const input = document.body.querySelector("input");
  ok(input instanceof HTMLInputElement);
  equal(input.value, "nomatch");
  const ul = document.body.querySelector("ul");
  ok(!ul);
});

test("AutocompleteInput: renders with matching suggestions", () => {
  mount(AutocompleteInput, {
    target: document.body,
    props: {
      value: "app",
      placeholder: "test placeholder",
      suggestions: ["apple", "banana", "cherry"],
    },
  });
  flushSync();
  const input = document.body.querySelector("input");
  ok(input instanceof HTMLInputElement);
  equal(input.value, "app");
  const ul = document.body.querySelector("ul");
  equal(ul?.firstElementChild?.textContent, "apple");
});
