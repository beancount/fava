<script>
  import { _ } from "../i18n";

  import { currencies } from "../stores";
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import AccountInput from "./AccountInput.svelte";

  /** @type {import("../entries").Posting} */
  export let posting;
  /** @type {number} */
  export let index;
  /** @type {string[]} */
  export let suggestions;
  /** @type {(arg: {from: number; to: number}) => void} */
  export let move;
  /** @type {() => void} */
  export let remove;
  /** @type {() => void} */
  export let add;

  $: amount_number = posting.amount.replace(/[^\-?0-9.]/g, "");
  $: amountSuggestions = $currencies.map((c) => `${amount_number} ${c}`);

  let drag = false;
  let draggable = true;
  /**
   * @param {MouseEvent} event
   */
  function mousemove(event) {
    draggable = !(event.target instanceof HTMLInputElement);
  }
  /**
   * @param {DragEvent} event
   */
  function dragstart(event) {
    event.dataTransfer?.setData("fava/posting", `${index}`);
  }
  /**
   * @param {DragEvent} event
   */
  function dragenter(event) {
    if (event.dataTransfer?.types.includes("fava/posting")) {
      event.preventDefault();
      drag = true;
    }
  }
  function dragleave() {
    drag = false;
  }
  /**
   * @param {DragEvent} event
   */
  function drop(event) {
    const from = event.dataTransfer?.getData("fava/posting");
    if (from) {
      move({ from: +from, to: index });
      drag = false;
    }
  }
</script>

<div
  class="flex-row"
  class:drag
  {draggable}
  on:mousemove={mousemove}
  on:dragstart={dragstart}
  on:dragenter={dragenter}
  on:dragover={dragenter}
  on:dragleave={dragleave}
  on:drop|preventDefault={drop}
>
  <button
    class="muted round remove-row"
    on:click={remove}
    type="button"
    tabindex={-1}
  >
    ×
  </button>
  <AccountInput className="grow" bind:value={posting.account} {suggestions} />
  <AutocompleteInput
    className="amount"
    placeholder={_("Amount")}
    suggestions={amountSuggestions}
    bind:value={posting.amount}
  />
  <button
    class="muted round add-row"
    type="button"
    on:click={add}
    title={_("Add posting")}
  >
    +
  </button>
</div>

<style>
  .drag {
    box-shadow: 0 0 5px var(--color-text);
  }

  div {
    padding-left: 50px;
    cursor: grab;
  }

  div > * {
    cursor: initial;
  }

  div .add-row {
    display: none;
  }

  div:last-child .add-row {
    display: initial;
  }

  div :global(.amount) {
    width: 220px;
  }

  div:last-child :global(.amount) {
    width: 192px;
  }

  @media (max-width: 767px) {
    div {
      padding-left: 0;
    }
  }
</style>
