import { deepEqual, equal, ok } from "node:assert/strict";
import { test } from "node:test";

import { range } from "d3-array";
import { type ComponentProps, flushSync, mount, unmount } from "svelte";

import AutocompleteInput from "../src/components/AutocompleteInput.svelte";
import { setup_jsdom, user_events } from "./dom.ts";

test.beforeEach(setup_jsdom);

/** Mount the `AutocompleteInput` component, with some defaults if not set and return the `<input>`. */
function mount_autocomplete(
  t: test.TestContext,
  props: Partial<ComponentProps<typeof AutocompleteInput>>,
): HTMLInputElement {
  const component = mount(AutocompleteInput, {
    target: document.body,
    props: {
      value: "",
      placeholder: "placeholder",
      suggestions: ["apple", "banana", "cherry"],
      ...props,
    },
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

/** Get the selected suggestion */
const selected = () =>
  document.body.querySelector("li[aria-selected=true]")?.textContent;

test("AutocompleteInput: renders no suggestions if none match", (t) => {
  const input = mount_autocomplete(t, { value: "nomatch" });
  equal(input.value, "nomatch");
  user_events.focus(input);

  deepEqual(suggestion_texts(), []);
});

test("AutocompleteInput: renders with matching suggestions", (t) => {
  const input = mount_autocomplete(t, { value: "app" });
  user_events.focus(input);

  deepEqual(suggestion_texts(), ["apple"]);
});

test("AutocompleteInput: does not show a single suggestion that already equals the value", (t) => {
  const input = mount_autocomplete(t, { value: "apple" });
  user_events.focus(input);

  deepEqual(suggestion_texts(), []);
});

test("AutocompleteInput: typing filters and updates suggestions", (t) => {
  const input = mount_autocomplete(t, {});
  user_events.focus(input);
  deepEqual(suggestion_texts(), ["apple", "banana", "cherry"]);

  user_events.type(input, "ban");
  deepEqual(suggestion_texts(), ["banana"]);
});

test("AutocompleteInput: ArrowDown/ArrowUp cycle through suggestions", (t) => {
  const input = mount_autocomplete(t, {
    suggestions: ["apple", "apricot", "avocado"],
  });
  user_events.type(input, "a");

  equal(selected(), undefined);
  user_events.keydown(input, "ArrowDown");
  equal(selected(), "apple");
  user_events.keydown(input, "ArrowDown");
  equal(selected(), "apricot");
  user_events.keydown(input, "ArrowDown");
  equal(selected(), "avocado");
  // wraps around to the first suggestion again.
  user_events.keydown(input, "ArrowDown");
  equal(selected(), "apple");

  // ArrowUp wraps around to the last suggestion.
  user_events.keydown(input, "ArrowUp");
  equal(selected(), "avocado");
  user_events.keydown(input, "ArrowUp");
  equal(selected(), "apricot");
});

test("AutocompleteInput: typing resets the highlighted suggestion", (t) => {
  const input = mount_autocomplete(t, {
    suggestions: ["apple", "apricot", "avocado"],
  });
  user_events.type(input, "a");
  user_events.keydown(input, "ArrowDown");
  user_events.keydown(input, "ArrowDown");
  equal(selected(), "apricot");

  user_events.type(input, "av");
  equal(selected(), undefined);
});

test("AutocompleteInput: automatic selection highlights the first suggestion", (t) => {
  const input = mount_autocomplete(t, {
    suggestions: ["apple", "apricot", "avocado"],
    automatic_selection: true,
  });
  // The list is only shown (and hence a suggestion highlighted) once open.
  equal(selected(), undefined);

  user_events.focus(input);
  equal(selected(), "apple");

  // Typing highlights the first of the updated suggestions.
  user_events.type(input, "av");
  deepEqual(suggestion_texts(), ["avocado"]);
  equal(selected(), "avocado");

  // Without any matching suggestion, nothing is highlighted.
  user_events.type(input, "nomatch");
  deepEqual(suggestion_texts(), []);
  equal(selected(), undefined);
});

test("AutocompleteInput: automatic selection allows moving to other suggestions", (t) => {
  const input = mount_autocomplete(t, {
    suggestions: ["apple", "apricot", "avocado"],
    automatic_selection: true,
  });
  user_events.type(input, "a");
  equal(selected(), "apple");

  user_events.keydown(input, "ArrowDown");
  equal(selected(), "apricot");
  // ArrowUp from the automatically highlighted first suggestion wraps around.
  user_events.keydown(input, "ArrowUp");
  equal(selected(), "apple");
  user_events.keydown(input, "ArrowUp");
  equal(selected(), "avocado");
});

test("AutocompleteInput: Enter selects the automatically highlighted suggestion", (t) => {
  const onenter = t.mock.fn();
  const onselect = t.mock.fn();
  const input = mount_autocomplete(t, {
    automatic_selection: true,
    onenter,
    onselect,
  });
  user_events.type(input, "ban");

  user_events.keydown(input, "Enter");
  equal(input.value, "banana");
  equal(onselect.mock.callCount(), 1);
  equal(onenter.mock.callCount(), 0);
});

test("AutocompleteInput: Tab selects the automatically highlighted suggestion", (t) => {
  const onselect = t.mock.fn();
  const onchange = t.mock.fn();
  const input = mount_autocomplete(t, {
    automatic_selection: true,
    onselect,
    onchange,
  });
  user_events.type(input, "ban");
  user_events.keydown(input, "Tab");
  user_events.blur(input);

  equal(input.value, "banana");
  equal(onselect.mock.callCount(), 1);
  equal(onchange.mock.callCount(), 1);
  deepEqual(onchange.mock.calls[0]?.arguments, ["banana"]);
  deepEqual(suggestion_texts(), []);
});

test("AutocompleteInput: blur without Tab does not select the automatically highlighted suggestion", (t) => {
  // On mobile, blur can happen for reasons other than explicit confirmation
  // and there is no Escape key to back out of an unwanted selection, so
  // only leaving via Tab should trigger automatic selection.
  const onselect = t.mock.fn();
  const onchange = t.mock.fn();
  const input = mount_autocomplete(t, {
    automatic_selection: true,
    onselect,
    onchange,
  });
  user_events.type(input, "ban");
  user_events.blur(input);

  equal(input.value, "ban");
  equal(onselect.mock.callCount(), 0);
  equal(onchange.mock.callCount(), 1);
  deepEqual(onchange.mock.calls[0]?.arguments, ["ban"]);
});

test("AutocompleteInput: blur does not select a suggestion of a closed list", (t) => {
  const onselect = t.mock.fn();
  const onchange = t.mock.fn();
  const input = mount_autocomplete(t, {
    automatic_selection: true,
    onselect,
    onchange,
  });
  user_events.type(input, "ban");
  user_events.keydown(input, "Escape");
  user_events.blur(input);

  equal(input.value, "ban");
  equal(onselect.mock.callCount(), 0);
  equal(onchange.mock.callCount(), 1);
  deepEqual(onchange.mock.calls[0]?.arguments, ["ban"]);
});

test("AutocompleteInput: blur does not select a suggestion with manual selection", (t) => {
  const onselect = t.mock.fn();
  const onchange = t.mock.fn();
  const input = mount_autocomplete(t, { onselect, onchange });
  user_events.type(input, "ban");
  user_events.keydown(input, "ArrowDown");
  equal(selected(), "banana");

  user_events.blur(input);
  equal(input.value, "ban");
  equal(onselect.mock.callCount(), 0);
  equal(onchange.mock.callCount(), 1);
});

test("AutocompleteInput: automatic selection does not highlight in a closed list", (t) => {
  const onenter = t.mock.fn();
  const onselect = t.mock.fn();
  const input = mount_autocomplete(t, {
    automatic_selection: true,
    onenter,
    onselect,
  });
  user_events.type(input, "ban");
  equal(selected(), "banana");

  user_events.keydown(input, "Escape");
  equal(selected(), undefined);

  // With the list closed, Enter does not select the first suggestion.
  user_events.keydown(input, "Enter");
  equal(input.value, "ban");
  equal(onselect.mock.callCount(), 0);
  equal(onenter.mock.callCount(), 1);

  // Reopening the list highlights the first suggestion again.
  user_events.keydown(input, "ArrowDown", { altKey: true });
  equal(selected(), "banana");
});

test("AutocompleteInput: Enter selects the highlighted suggestion", (t) => {
  const onselect = t.mock.fn();
  const onenter = t.mock.fn();
  const onchange = t.mock.fn();
  const input = mount_autocomplete(t, { onenter, onselect, onchange });
  user_events.type(input, "ba");
  user_events.keydown(input, "ArrowDown");
  const not_prevented = user_events.keydown(input, "Enter");

  equal(not_prevented, false);
  equal(input.value, "banana");
  equal(onenter.mock.callCount(), 0);
  equal(onselect.mock.callCount(), 1);
  equal(onchange.mock.callCount(), 1);
  deepEqual(suggestion_texts(), []);
});

test("AutocompleteInput: Enter without a highlighted suggestion calls onenter instead", (t) => {
  const onenter = t.mock.fn();
  const onselect = t.mock.fn();
  const onchange = t.mock.fn();
  const input = mount_autocomplete(t, { onenter, onselect, onchange });
  user_events.type(input, "ba");
  equal(onenter.mock.callCount(), 0);
  equal(onselect.mock.callCount(), 0);
  equal(onchange.mock.callCount(), 0);

  user_events.keydown(input, "Enter");
  equal(onenter.mock.callCount(), 1);
  equal(onselect.mock.callCount(), 0);
  equal(onchange.mock.callCount(), 1);
  equal(input.value, "ba");
});

test("AutocompleteInput: mousedown on a suggestion selects it", (t) => {
  const onselect = t.mock.fn();
  const onchange = t.mock.fn();
  const input = mount_autocomplete(t, { onselect, onchange });
  user_events.type(input, "cher");
  const li = document.body.querySelector("li");
  ok(li);
  user_events.mousedown(li, { button: 0 });

  equal(input.value, "cherry");
  equal(onselect.mock.callCount(), 1);
  equal(onchange.mock.callCount(), 1);
});

test("AutocompleteInput: mousedown with a non-primary button does not select", (t) => {
  const onselect = t.mock.fn();
  const onchange = t.mock.fn();
  const input = mount_autocomplete(t, { onselect, onchange });
  user_events.type(input, "cher");
  const li = document.body.querySelector("li");
  ok(li);
  user_events.mousedown(li, { button: 2 });

  equal(input.value, "cher");
  equal(onselect.mock.callCount(), 0);
  equal(onchange.mock.callCount(), 0);
});

test("AutocompleteInput: Escape closes an open suggestion list without clearing the value", (t) => {
  const onselect = t.mock.fn();
  const onchange = t.mock.fn();
  const input = mount_autocomplete(t, { onselect, onchange });
  user_events.type(input, "app");
  deepEqual(suggestion_texts(), ["apple"]);

  equal(user_events.keydown(input, "Escape"), false);

  equal(input.value, "app");
  deepEqual(suggestion_texts(), []);
  equal(onselect.mock.callCount(), 0);
  equal(onchange.mock.callCount(), 0);
});

test("AutocompleteInput: Escape clears the value when the suggestion list is closed", (t) => {
  const onselect = t.mock.fn();
  const onchange = t.mock.fn();
  const input = mount_autocomplete(t, { value: "app", onselect, onchange });
  deepEqual(suggestion_texts(), []);

  equal(user_events.keydown(input, "Escape"), false);

  equal(input.value, "");
  equal(onselect.mock.callCount(), 0);
  equal(onchange.mock.callCount(), 0);

  user_events.blur(input);
  equal(onselect.mock.callCount(), 0);
  equal(onchange.mock.callCount(), 1);
});

test("AutocompleteInput: Escape is not handled if there is nothing to dismiss", (t) => {
  // Otherwise the modal that the input is in could not be closed with Escape.
  const input = mount_autocomplete(t, { value: "" });
  deepEqual(suggestion_texts(), []);

  ok(user_events.keydown(input, "Escape"));
  equal(input.value, "");
});

test("AutocompleteInput: (Alt+)ArrowDown opens the suggestion list and Alt+ArrowUp closes it", (t) => {
  const input = mount_autocomplete(t, { value: "app" });
  deepEqual(suggestion_texts(), []);

  user_events.keydown(input, "ArrowDown");
  deepEqual(suggestion_texts(), ["apple"]);

  user_events.keydown(input, "ArrowUp", { altKey: true });
  deepEqual(suggestion_texts(), []);

  user_events.keydown(input, "ArrowDown", { altKey: true });
  deepEqual(suggestion_texts(), ["apple"]);

  user_events.keydown(input, "ArrowUp", { altKey: true });
  deepEqual(suggestion_texts(), []);
});

test("AutocompleteInput: blur hides the suggestion list and fires onchange", (t) => {
  const onchange = t.mock.fn();
  const input = mount_autocomplete(t, { onchange });
  deepEqual(suggestion_texts(), []);

  user_events.focus(input);
  deepEqual(suggestion_texts(), ["apple", "banana", "cherry"]);

  user_events.blur(input);
  equal(onchange.mock.callCount(), 1);
  deepEqual(suggestion_texts(), []);
});

test("AutocompleteInput: clear_button is only shown when there is a value and clears it on click", (t) => {
  const onchange = t.mock.fn();
  const input = mount_autocomplete(t, { clear_button: true, onchange });
  ok(!document.body.querySelector("button"));

  user_events.type(input, "app");
  const button = document.body.querySelector("button");
  ok(button);

  user_events.click(button);

  equal(input.value, "");
  equal(onchange.mock.callCount(), 1);
  ok(!document.body.querySelector("button"));
});

test("AutocompleteInput: value_extractor and value_selector operate on a substring of the value", (t) => {
  // Simulate autocompleting the last comma-separated tag of the value.
  const value_extractor = t.mock.fn(
    (val: string, _input: HTMLInputElement): string =>
      val.split(",").at(-1) ?? "",
  );
  const value_selector = t.mock.fn(
    (selected: string, el: HTMLInputElement): string => {
      const parts = el.value.split(",");
      parts[parts.length - 1] = selected;
      return parts.join(",");
    },
  );

  const input = mount_autocomplete(t, {
    value: "foo,ba",
    value_extractor,
    value_selector,
  });
  user_events.focus(input);

  deepEqual(suggestion_texts(), ["banana"]);
  deepEqual(value_extractor.mock.calls[0]?.arguments, ["foo,ba", input]);

  const li = document.body.querySelector("li");
  ok(li);
  user_events.mousedown(li, { button: 0 });

  equal(input.value, "foo,banana");
  equal(value_selector.mock.callCount(), 1);
  deepEqual(value_selector.mock.calls[0]?.arguments, ["banana", input]);
});

test("AutocompleteInput: check_validity sets a custom validity message on the input", (t) => {
  const check_validity = t.mock.fn((val: string): string =>
    val === "invalid" ? "not a valid value" : "",
  );

  const input = mount_autocomplete(t, { value: "invalid", check_validity });
  equal(input.validationMessage, "not a valid value");
  equal(input.checkValidity(), false);
  equal(check_validity.mock.callCount(), 1);
  deepEqual(check_validity.mock.calls[0]?.arguments, ["invalid"]);

  user_events.type(input, "valid");
  equal(input.validationMessage, "");
  equal(input.checkValidity(), true);
  equal(check_validity.mock.callCount(), 2);
  deepEqual(check_validity.mock.calls[1]?.arguments, ["valid"]);
});

test("AutocompleteInput: required prop is reflected on the input", (t) => {
  const input = mount_autocomplete(t, { required: true });
  ok(input.required);
});

test("AutocompleteInput: limits suggestions to 30 matches", (t) => {
  const suggestions = range(50).map((i) => `item${i.toString()}`);
  const input = mount_autocomplete(t, { suggestions });
  user_events.focus(input);
  deepEqual(suggestion_texts(), suggestions.slice(0, 30));
});
