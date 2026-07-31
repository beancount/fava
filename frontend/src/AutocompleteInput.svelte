<!--
  @component
  An autocomplete input for fuzzy selection of suggestions.

  It receives its `value` and a list of possible `suggestions`. Matching suggestions will be
  shown in a dropdown below the input field and can be selected by clicking or by keyboard.

  This is an implementation of the Combobox pattern as described by the
  ARIA Authoring Practices Guide (APG) at
    https://www.w3.org/WAI/ARIA/apg/patterns/combobox/
  In particular it should match the Editable Combobox With List Autocomplete example at
    https://www.w3.org/WAI/ARIA/apg/patterns/combobox/examples/combobox-autocomplete-list/
-->
<script lang="ts">
  import type { KeySpec } from "./keyboard-shortcuts.ts";
  import { keyboardShortcut, normalise_key } from "./keyboard-shortcuts.ts";
  import { fuzzyfilter, fuzzywrap } from "./lib/fuzzy.ts";

  interface Props {
    /** The currently entered value (bindable). */
    value: string;
    /** A placeholder for the input field. */
    placeholder: string;
    /** The suggestions for the value. */
    suggestions?: readonly string[] | undefined;
    /** A function to extract the string that should be used for suggestion filtering. */
    valueExtractor?: (val: string, input: HTMLInputElement) => string;
    /** A function to update the value after selecting a suggestion. */
    valueSelector?: (val: string, input: HTMLInputElement) => string;
    /** Automatically adjust the size of the input element. */
    setSize?: boolean;
    /** A key binding to add for this input. */
    key?: KeySpec;
    /** A function that checks the entered value for validity. */
    checkValidity?: (val: string) => string;
    /** Whether to mark the input as required. */
    required?: boolean | undefined;
    /** Whether to show a button to clear the input. */
    clearButton?: boolean;
    /** An event handler to run on enter. */
    onenter?: () => void;
    /** An event handler to run on an element being selected. */
    onselect?: () => void;
    /** An event handler to run whenever the value changes (on select, enter, or blur). */
    onchange?: (value: string) => void;
  }

  let {
    value = $bindable(),
    placeholder,
    suggestions = [],
    valueExtractor,
    valueSelector,
    setSize = false,
    key,
    checkValidity,
    clearButton = false,
    required,
    onenter,
    onselect,
    onchange,
  }: Props = $props();

  const uid = $props.id();
  const autocomple_id = `combobox-autocomplete-${uid}`;

  let hidden = $state.raw(true);
  let index = $state.raw(-1);
  let input: HTMLInputElement | undefined = $state.raw();

  let extracted_value = $derived(
    input && valueExtractor ? valueExtractor(value, input) : value,
  );
  let filtered_suggestions: string[] = $derived.by(() => {
    const filtered = fuzzyfilter(extracted_value, suggestions).slice(0, 30);
    return filtered.length === 1 && filtered[0] === extracted_value
      ? []
      : filtered;
  });

  $effect(() => {
    const msg = checkValidity ? checkValidity(value) : "";
    input?.setCustomValidity(msg);
  });

  $effect.pre(() => {
    // ensure the index is pointing to a valid element.
    index = Math.min(index, filtered_suggestions.length - 1);
  });

  export function blur(): void {
    input?.blur();
  }

  function select(suggestion: string) {
    value =
      input && valueSelector ? valueSelector(suggestion, input) : suggestion;
    onchange?.(value);
    onselect?.();
    hidden = true;
  }

  let expanded = $derived(!hidden && filtered_suggestions.length > 0);
  let active_suggestion = $derived(
    expanded && index > -1 ? filtered_suggestions[index] : undefined,
  );
  let active_id = $derived(
    expanded && index > -1 ? `${autocomple_id}-${index.toString()}` : undefined,
  );

  function onkeydown(event: KeyboardEvent) {
    const key = normalise_key(event);
    if (key === "Enter") {
      if (active_suggestion != null) {
        select(active_suggestion);
      } else {
        onchange?.(value);
        onenter?.();
        return;
      }
    } else if (key === "Escape") {
      if (expanded) {
        index = -1;
        hidden = true;
      } else {
        value = "";
      }
    } else if (key === "ArrowUp") {
      if (expanded) {
        index = index <= 0 ? filtered_suggestions.length - 1 : index - 1;
      }
    } else if (key === "ArrowDown") {
      if (expanded) {
        index = index === filtered_suggestions.length - 1 ? 0 : index + 1;
      } else {
        hidden = false;
      }
    } else if (key === "Alt+ArrowDown") {
      hidden = false;
    } else if (key === "Alt+ArrowUp") {
      hidden = true;
    } else {
      return;
    }
    event.preventDefault();
    event.stopPropagation();
  }
</script>

<span>
  <input
    type="text"
    autocomplete="off"
    role="combobox"
    class={{ "content-sized": setSize }}
    aria-expanded={expanded}
    aria-controls={autocomple_id}
    aria-autocomplete="list"
    aria-activedescendant={active_id}
    bind:value
    bind:this={input}
    {@attach keyboardShortcut(key)}
    onblur={() => {
      onchange?.(value);
      hidden = true;
    }}
    onfocus={() => {
      hidden = false;
    }}
    oninput={() => {
      hidden = false;
    }}
    {onkeydown}
    {placeholder}
    {required}
  />
  {#if clearButton && value}
    <button
      type="button"
      tabindex={-1}
      class="muted round"
      onclick={() => {
        value = "";
        onchange?.(value);
      }}
    >
      ×
    </button>
  {/if}
  {#if expanded}
    <ul role="listbox" id={autocomple_id}>
      {#each filtered_suggestions as suggestion, i (suggestion)}
        <li
          id={`${autocomple_id}-${i.toString()}`}
          role="option"
          aria-selected={i === index}
          onmousedown={(event) => {
            if (event.button === 0) {
              select(suggestion);
            }
          }}
        >
          {#each fuzzywrap(extracted_value, suggestion) as [type, text], i (i)}
            {#if type === "text"}
              {text}
            {:else}
              <span>{text}</span>
            {/if}
          {/each}
        </li>
      {/each}
    </ul>
  {/if}
</span>

<style>
  span {
    position: relative;
    display: inline-block;
    flex: var(--autocomplete-wrapper-flex, initial);
  }

  input {
    width: 100%;
  }

  input.content-sized {
    min-width: calc(8rem + 2px);
    field-sizing: content;
  }

  ul {
    position: var(--autocomplete-list-position, absolute);
    z-index: var(--z-index-autocomplete);
    overflow: hidden auto;
    background-color: var(--background);
    border: 1px solid var(--border-darker);
    box-shadow: var(--box-shadow-dropdown);
  }

  li {
    min-width: 8rem;
    padding: 0 0.5em;
    white-space: nowrap;
    cursor: pointer;
  }

  li:hover {
    color: var(--background);
    background-color: var(--link-color-lighter);
  }

  li[aria-selected="true"] {
    color: var(--background);
    background-color: var(--link-color);
  }

  button {
    position: absolute;
    top: 8px;
    right: 4px;
    background: transparent;
  }

  li span {
    height: 1.2em;
    padding: 0 0.05em;
    margin: 0 -0.05em;
    background-color: var(--autocomplete-match);
    border-radius: 2px;
  }

  @media print {
    button {
      display: none;
    }
  }
</style>
