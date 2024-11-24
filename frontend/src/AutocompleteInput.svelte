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
<script lang="ts" module>
  /** Incrementing number to use for element ids in the component. */
  let id = 0;
</script>

<script lang="ts">
  import type { KeySpec } from "./keyboard-shortcuts";
  import { keyboardShortcut } from "./keyboard-shortcuts";
  import { fuzzyfilter, fuzzywrap, type FuzzyWrappedText } from "./lib/fuzzy";

  interface Props {
    /** The currently entered value (bindable). */
    value: string;
    /** A placeholder for the input field. */
    placeholder: string;
    /** The suggestions for the value. */
    suggestions: readonly string[];
    /** A function to extract the string that should be used for suggestion filtering. */
    valueExtractor?: (val: string, input: HTMLInputElement) => string;
    /** A function to update the value after selecting a suggestion. */
    valueSelector?: (val: string, input: HTMLInputElement) => string;
    /** Automatically adjust the size of the input element. */
    setSize?: boolean;
    /** An optional class name to assign to the input element. */
    className?: string;
    /** A key binding to add for this input. */
    key?: KeySpec;
    /** A function that checks the entered value for validity. */
    checkValidity?: (val: string) => string;
    /** Whether to show a button to clear the input. */
    clearButton?: boolean;
    /** An event handler to run on blur. */
    onBlur?: (el: HTMLInputElement) => void;
    /** An event handler to run on enter. */
    onEnter?: (el: HTMLInputElement) => void;
    /** An event handler to run on an element being selected. */
    onSelect?: (el: HTMLInputElement) => void;
  }

  let {
    value = $bindable(),
    placeholder,
    suggestions,
    valueExtractor,
    valueSelector,
    setSize = false,
    className,
    key,
    checkValidity,
    clearButton = false,
    onBlur,
    onEnter,
    onSelect,
  }: Props = $props();

  id += 1;
  const autocomple_id = `combobox-autocomplete-${id.toString()}`;

  let hidden = $state.raw(true);
  let index = $state.raw(-1);
  let input: HTMLInputElement | undefined = $state.raw();

  let size = $derived(
    setSize ? Math.max(value.length, placeholder.length) + 1 : undefined,
  );
  let extractedValue = $derived(
    input && valueExtractor ? valueExtractor(value, input) : value,
  );
  let filteredSuggestions: {
    suggestion: string;
    fuzzywrapped: FuzzyWrappedText;
  }[] = $derived.by(() => {
    const filtered = fuzzyfilter(extractedValue, suggestions)
      .slice(0, 30)
      .map((suggestion) => ({
        suggestion,
        fuzzywrapped: fuzzywrap(extractedValue, suggestion),
      }));
    return filtered.length === 1 && filtered[0]?.suggestion === extractedValue
      ? []
      : filtered;
  });

  $effect(() => {
    const msg = checkValidity ? checkValidity(value) : "";
    input?.setCustomValidity(msg);
  });

  $effect.pre(() => {
    // ensure the index is pointing to a valid element.
    index = Math.min(index, filteredSuggestions.length - 1);
  });

  function select(suggestion: string) {
    value =
      input && valueSelector ? valueSelector(suggestion, input) : suggestion;
    if (input) {
      onSelect?.(input);
    }
    hidden = true;
  }

  function mousedown(event: MouseEvent, suggestion: string) {
    if (event.button === 0) {
      select(suggestion);
    }
  }

  let expanded = $derived(!hidden && filteredSuggestions.length > 0);

  function keydown(event: KeyboardEvent) {
    if (event.key === "Enter") {
      const suggestion = filteredSuggestions[index]?.suggestion;
      if (index > -1 && !hidden && suggestion != null) {
        event.preventDefault();
        select(suggestion);
      } else if (input) {
        onEnter?.(input);
      }
    } else if (event.key === " " && event.ctrlKey) {
      hidden = false;
    } else if (event.key === "Escape") {
      event.stopPropagation();
      if (expanded) {
        index = -1;
        hidden = true;
      } else {
        value = "";
      }
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      index = index === 0 ? filteredSuggestions.length - 1 : index - 1;
    } else if (event.key === "ArrowDown") {
      event.preventDefault();
      index = index === filteredSuggestions.length - 1 ? 0 : index + 1;
    }
  }
</script>

<span class={className}>
  <input
    type="text"
    autocomplete="off"
    role="combobox"
    aria-expanded={expanded}
    aria-controls={autocomple_id}
    bind:value
    bind:this={input}
    use:keyboardShortcut={key}
    onblur={(event) => {
      hidden = true;
      onBlur?.(event.currentTarget);
    }}
    onfocus={() => {
      hidden = false;
    }}
    oninput={() => {
      hidden = false;
    }}
    onkeydown={keydown}
    {placeholder}
    {size}
  />
  {#if clearButton && value}
    <button
      type="button"
      tabindex={-1}
      class="muted round"
      onclick={() => {
        value = "";
        if (input) {
          onSelect?.(input);
        }
      }}
    >
      ×
    </button>
  {/if}
  {#if filteredSuggestions.length}
    <ul {hidden} role="listbox" id={autocomple_id}>
      {#each filteredSuggestions as { fuzzywrapped, suggestion }, i}
        <li
          role="option"
          aria-selected={i === index}
          class:selected={i === index}
          onmousedown={(ev) => {
            mousedown(ev, suggestion);
          }}
        >
          {#each fuzzywrapped as [type, text]}
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
  }

  input {
    width: 100%;
  }

  ul {
    position: absolute;
    z-index: var(--z-index-autocomplete);
    overflow: hidden auto;
    background-color: var(--background);
    border: 1px solid var(--border-darker);
    box-shadow: var(--box-shadow-dropdown);
  }

  :global(aside) ul {
    /* the only way to get the list to overflow the
       aside is to put it in fixed position */
    position: fixed;
  }

  li {
    min-width: 8rem;
    padding: 0 0.5em;
    white-space: nowrap;
    cursor: pointer;
  }

  li.selected,
  li:hover {
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
