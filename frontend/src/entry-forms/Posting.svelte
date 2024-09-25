<script lang="ts">
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import type { Posting } from "../entries";
  import { _ } from "../i18n";
  import { currencies } from "../stores";
  import AccountInput from "./AccountInput.svelte";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadata from "./EntryMetadata.svelte";

  export let posting: Posting;
  export let index: number;
  export let suggestions: string[] | undefined;
  export let date: string | undefined;
  export let move: (arg: { from: number; to: number }) => void;
  export let remove: () => void;

  $: amount_number = posting.amount.replace(/[^\-?0-9.]/g, "");
  $: amountSuggestions = $currencies.map((c) => `${amount_number} ${c}`);

  let drag = false;
  let draggable = true;

  function mousemove(event: MouseEvent) {
    draggable = !(event.target instanceof HTMLInputElement);
  }
  function dragstart(event: DragEvent) {
    event.dataTransfer?.setData("fava/posting", index.toString());
  }
  function dragenter(event: DragEvent) {
    const types = event.dataTransfer?.types ?? [];
    if (types.includes("fava/posting")) {
      event.preventDefault();
      drag = true;
    }
  }
  function dragleave() {
    drag = false;
  }
  function drop(event: DragEvent) {
    const from = event.dataTransfer?.getData("fava/posting");
    if (from != null) {
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
  role="group"
>
  <button
    type="button"
    class="muted round remove-row"
    on:click={remove}
    tabindex={-1}
  >
    ×
  </button>
  <AccountInput
    className="grow"
    bind:value={posting.account}
    {suggestions}
    {date}
  />
  <AutocompleteInput
    className="amount"
    placeholder={_("Amount")}
    suggestions={amountSuggestions}
    bind:value={posting.amount}
  />
  <AddMetadataButton bind:meta={posting.meta} />
  <EntryMetadata bind:meta={posting.meta} />
</div>

<style>
  .drag {
    box-shadow: var(--box-shadow-button);
  }

  div {
    padding-left: 50px;
    cursor: grab;
  }

  div > * {
    cursor: initial;
  }

  div:last-child .remove-row {
    visibility: hidden;
  }

  div :global(.amount) {
    width: 220px;
  }

  @media (width <= 767px) {
    div {
      padding-left: 0;
    }
  }
</style>
