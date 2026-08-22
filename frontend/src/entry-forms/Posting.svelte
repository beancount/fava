<script lang="ts">
  import type { EntryMetadata, Posting } from "../entries/index.ts";
  import AccountInput from "./AccountInput.svelte";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import AmountInput from "./AmountInput.svelte";
  import EntryMetadataSvelte from "./EntryMetadata.svelte";

  interface Props {
    /** The posting to show and edit. */
    posting: Posting;
    /** Index in the list of postings, used to move it. */
    index: number;
    /** Account suggestions. */
    suggestions?: readonly string[] | undefined;
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

  let drag = $state.raw(false);
  let draggable = $state.raw(true);

  function onmousemove(event: MouseEvent) {
    draggable = !(event.target instanceof HTMLInputElement);
  }
  function ondragstart(event: DragEvent) {
    event.dataTransfer?.setData("fava/posting", index.toString());
  }
  function ondragenter(event: DragEvent) {
    const types = event.dataTransfer?.types ?? [];
    if (types.includes("fava/posting")) {
      event.preventDefault();
      drag = true;
    }
  }
  function ondragleave() {
    drag = false;
  }
  function ondrop(event: DragEvent) {
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
  {onmousemove}
  {ondragstart}
  {ondragenter}
  ondragover={ondragenter}
  {ondragleave}
  {ondrop}
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
    bind:value={
      () => posting.account,
      (account: string) => {
        posting = posting.set("account", account);
      }
    }
    {suggestions}
    {date}
    --autocomplete-wrapper-flex="2"
  />
  <AmountInput
    bind:value={
      () => posting.amount,
      (amount: string) => {
        posting = posting.set("amount", amount);
      }
    }
    account={posting.account}
    --autocomplete-wrapper-flex="1"
  />
  <AddMetadataButton
    bind:meta={
      () => posting.meta,
      (meta: EntryMetadata) => {
        posting = posting.set("meta", meta);
      }
    }
  />
</div>
<EntryMetadataSvelte
  bind:meta={
    () => posting.meta,
    (meta: EntryMetadata) => {
      posting = posting.set("meta", meta);
    }
  }
/>

<style>
  .drag {
    box-shadow: var(--box-shadow-button);
  }

  div {
    padding-left: 3rem;
    cursor: grab;
  }

  div > * {
    cursor: initial;
  }

  div:last-child .remove-row {
    visibility: hidden;
  }

  @media (width <= 767px) {
    div {
      padding-left: 0;
    }
  }
</style>
