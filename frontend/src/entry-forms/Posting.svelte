<script lang="ts">
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import type { EntryMetadata, Posting } from "../entries";
  import { _ } from "../i18n";
  import { currencies } from "../stores";
  import AccountInput from "./AccountInput.svelte";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadataSvelte from "./EntryMetadata.svelte";

  interface Props {
    /** The posting to show and edit. */
    posting: Posting;
    /** Index in the list of postings, used to move it. */
    index: number;
    /** Account suggestions. */
    suggestions?: string[] | undefined;
    /** Entry date to limit account suggestions. */
    date?: string;
    /** Handler to move a posting to another position on drag. */
    move: (arg: { from: number; to: number }) => void;
    /** Handler to remove this posting. */
    remove: () => void;
  }

  let {
    posting = $bindable(),
    index,
    suggestions,
    date,
    move,
    remove,
  }: Props = $props();

  let amount_number = $derived(posting.amount.replace(/[^\-?0-9.]/g, ""));
  let amountSuggestions = $derived(
    $currencies.map((c) => `${amount_number} ${c}`),
  );

  let drag = $state.raw(false);
  let draggable = $state.raw(true);

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
    event.preventDefault();
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
  onmousemove={mousemove}
  ondragstart={dragstart}
  ondragenter={dragenter}
  ondragover={dragenter}
  ondragleave={dragleave}
  ondrop={drop}
  role="group"
>
  <button
    type="button"
    class="muted round remove-row"
    onclick={remove}
    tabindex={-1}
  >
    ×
  </button>
  <AccountInput
    className="grow"
    bind:value={
      () => posting.account,
      (account: string) => {
        posting = posting.set("account", account);
      }
    }
    {suggestions}
    {date}
  />
  <AutocompleteInput
    className="amount"
    placeholder={_("Amount")}
    suggestions={amountSuggestions}
    bind:value={
      () => posting.amount,
      (amount: string) => {
        posting = posting.set("amount", amount);
      }
    }
  />
  <AddMetadataButton
    bind:meta={
      () => posting.meta,
      (meta: EntryMetadata) => {
        posting = posting.set("meta", meta);
      }
    }
  />
  <EntryMetadataSvelte
    bind:meta={
      () => posting.meta,
      (meta: EntryMetadata) => {
        posting = posting.set("meta", meta);
      }
    }
  />
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
