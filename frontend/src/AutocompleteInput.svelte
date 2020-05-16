<script>
  import { createEventDispatcher } from "svelte";
  import { fuzzyfilter, fuzzywrap } from "./lib/fuzzy";
  import { keyboardShortcut } from "./keyboard-shortcuts";

  const dispatch = createEventDispatcher();

  export let value;
  export let suggestions;
  export let name = "";
  export let placeholder = "";
  export let valueExtractor = null;
  export let valueSelector = null;
  export let setSize = false;
  export let className = null;
  export let key = null;
  export let checkValidity = null;
  export let clearButton = false;
  let filteredSuggestions = [];
  let hidden = true;
  let index = -1;
  let input;

  $: size = setSize ? Math.max(value.length, placeholder.length) + 1 : null;

  $: if (input && checkValidity) {
    input.setCustomValidity(checkValidity(value));
  }

  $: {
    const val = input && valueExtractor ? valueExtractor(value, input) : value;
    const filtered = fuzzyfilter(val, suggestions)
      .slice(0, 30)
      .map((suggestion) => ({
        suggestion,
        innerHTML: fuzzywrap(val, suggestion),
      }));
    filteredSuggestions =
      filtered.length === 1 && filtered[0].suggestion === val ? [] : filtered;
    index = Math.min(index, filteredSuggestions.length - 1);
  }

  function select(suggestion) {
    value =
      input && valueSelector ? valueSelector(suggestion, input) : suggestion;
    dispatch("select");
    hidden = true;
  }

  function mousedown(event, suggestion) {
    if (event.button === 0) {
      select(suggestion);
    }
  }

  function keydown(event) {
    if (event.key === "Enter") {
      if (index > -1) {
        event.preventDefault();
        select(filteredSuggestions[index].suggestion);
      }
    } else if (event.key === "Escape") {
      hidden = true;
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      index = index === 0 ? filteredSuggestions.length - 1 : index - 1;
    } else if (event.key === "ArrowDown") {
      event.preventDefault();
      index = index === filteredSuggestions.length - 1 ? 0 : index + 1;
    }
  }
</script>

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
    overflow-x: hidden;
    overflow-y: auto;
    background-color: var(--color-background);
    border: 1px solid var(--color-background-darkest);
    box-shadow: 0 3px 3px var(--color-background-darker);
  }

  li {
    min-width: 8rem;
    padding: 0 0.5em;
    white-space: nowrap;
    cursor: pointer;
  }

  li.selected,
  li:hover {
    color: var(--color-background);
    background-color: var(--color-links);
  }

  button {
    position: absolute;
    top: 8px;
    right: 4px;
    background: transparent;
  }

  li :global(span) {
    height: 1.2em;
    padding: 0 0.05em;
    margin: 0 -0.05em;
    background-color: var(--color-autocomplete-match);
    border-radius: 2px;
  }
</style>

<span class={className}>
  <input
    {name}
    type="text"
    autocomplete="off"
    bind:value
    bind:this={input}
    use:keyboardShortcut={key}
    on:blur={() => {
      hidden = true;
      dispatch('blur');
    }}
    on:focusin={() => {
      hidden = false;
    }}
    on:input={() => {
      hidden = false;
    }}
    on:keydown={keydown}
    {placeholder}
    {size} />
  {#if clearButton && value}
    <button
      type="button"
      tabindex="-1"
      class="muted round"
      on:click={() => {
        value = '';
        dispatch('select');
      }}>
      ×
    </button>
  {/if}
  {#if filteredSuggestions.length}
    <ul {hidden}>
      {#each filteredSuggestions as { innerHTML, suggestion }, i}
        <li
          class:selected={i === index}
          on:mousedown={(ev) => mousedown(ev, suggestion)}>
          {@html innerHTML}
        </li>
      {/each}
    </ul>
  {/if}
</span>
