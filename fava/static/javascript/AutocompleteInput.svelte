<script>
  import { createEventDispatcher } from "svelte";
  import { fuzzytest, fuzzywrap } from "./helpers";

  const dispatch = createEventDispatcher();

  export let value = "";
  export let suggestions = [];
  export let name = "";
  export let placeholder = "";
  export let valueExtractor;
  export let valueSelector;
  export let setSize = false;
  let filteredSuggestions = [];
  let hidden = true;
  let index = -1;
  let input;

  export function focus() {
    input.focus();
  }

  export function setCustomValidity(str) {
    input.setCustomValidity(str);
  }

  $: if (index > filteredSuggestions.length - 1) {
    index = filteredSuggestions.length - 1;
  }

  $: {
    const val = input && valueExtractor ? valueExtractor(value, input) : value;
    const filtered = suggestions
      .map(suggestion => String(suggestion))
      .filter(suggestion => fuzzytest(val, suggestion))
      .slice(0, 30)
      .map(suggestion => ({
        suggestion,
        innerHTML: fuzzywrap(val, suggestion),
      }));
    if (filtered.length === 1 && filtered[0].suggestion === val) {
      filteredSuggestions = [];
    } else {
      filteredSuggestions = filtered;
    }
  }

  function select(suggestion) {
    if (input && valueSelector) {
      value = valueSelector(suggestion, input);
    } else {
      value = suggestion;
    }
    dispatch("select");
    hidden = true;
  }

  function mousedown(event, suggestion) {
    if (event.button === 0) {
      select(suggestion);
    }
  }

  function keydown(event) {
    if (event.keyCode === 13) {
      // ENTER
      if (index > -1) {
        event.preventDefault();
        select(filteredSuggestions[index].suggestion);
      }
    } else if (event.keyCode === 27) {
      hidden = true;
      // ESC
    } else if (event.keyCode === 38) {
      // UP
      event.preventDefault();
      index = index === 0 ? filteredSuggestions.length - 1 : index - 1;
    } else if (event.keyCode === 40) {
      // DOWN
      event.preventDefault();
      index = index === filteredSuggestions.length - 1 ? 0 : index + 1;
    }
  }

  const inputOptions = {};

  $: if (setSize) {
    inputOptions.size = Math.max(value.length, placeholder.length) + 1;
  }
  /*
    if (this.list === "accounts" && this.input.closest(".entry-form")) {
      const payeeInput = select(
        "input[name=payee]",
        this.input.closest(".entry-form")
      );
      if (payeeInput) {
        const payee = payeeInput.value.trim();
        if (accountCompletionCache[payee]) {
          return accountCompletionCache[payee];
        }
        const suggestions = await fetchAPI("payee_accounts", { payee });
        accountCompletionCache[payee] = suggestions;
        return suggestions;
      }
    }
    */
</script>

<style>
  span {
    position: relative;
  }

  .autocomplete {
    position: fixed;
    float: left;
  }
</style>

<span>
  <input
    {name}
    type="text"
    autocomplete="off"
    bind:value
    bind:this={input}
    on:blur={() => {
      hidden = true;
    }}
    on:focusin={() => {
      hidden = false;
    }}
    on:input={() => {
      hidden = false;
    }}
    on:keydown={keydown}
    {placeholder}
    {...inputOptions} />
  <ul class="autocomplete" {hidden}>
    {#each filteredSuggestions as { innerHTML, suggestion }, i}
      <li
        class:selected={i === index}
        on:mousedown={ev => mousedown(ev, suggestion)}>
        {@html innerHTML}
      </li>
    {/each}
  </ul>
</span>
