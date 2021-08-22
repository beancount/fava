<script lang="ts">
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import type { Posting } from "../entries";
  import { _ } from "../i18n";
  import { currencies } from "../stores";

  import AccountInput from "./AccountInput.svelte";

  export let posting: Posting;
  export let index: number;
  export let suggestions: string[] | undefined;
  export let move: (arg: { from: number; to: number }) => void;
  export let remove: () => void;
  export let add: () => void;

  $: amount_number = posting.amount.replace(/[^\-?0-9.]/g, "");
  $: amountSuggestions = $currencies.map((c) => `${amount_number} ${c}`);

  let drag = false;
  let draggable = true;

  function mousemove(event: MouseEvent) {
    draggable = !(event.target instanceof HTMLInputElement);
  }
  function dragstart(event: DragEvent) {
    event.dataTransfer?.setData("fava/posting", `${index}`);
  }
  function dragenter(event: DragEvent) {
    if (event.dataTransfer?.types.includes("fava/posting")) {
      event.preventDefault();
      drag = true;
    }
  }
  function dragleave() {
    drag = false;
  }
  function drop(event: DragEvent) {
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
