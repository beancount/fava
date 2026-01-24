<script lang="ts">
  import type { EntryMetadata, Posting } from "../entries/index.ts";
  import { _ } from "../i18n.ts";
  import { currencies } from "../stores/index.ts";
  import AccountInput from "./AccountInput.svelte";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadataSvelte from "./EntryMetadata.svelte";

  const DEFAULT_CURRENCY = "SGD";

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

  /** Parse the amount string into number and currency parts. */
  function parseAmount(amount: string): { number: string; currency: string } {
    const trimmed = amount.trim();
    if (!trimmed) {
      return { number: "", currency: DEFAULT_CURRENCY };
    }
    // Match patterns like "123.45 USD", "-50 EUR", "100USD", etc.
    const match = trimmed.match(/^(-?[\d.,]+)\s*([A-Za-z]*)$/);
    if (match) {
      return {
        number: match[1] ?? "",
        currency: match[2] || DEFAULT_CURRENCY,
      };
    }
    // Fallback: try to extract just the number
    const numberMatch = trimmed.match(/(-?[\d.,]+)/);
    return {
      number: numberMatch?.[1] ?? "",
      currency: DEFAULT_CURRENCY,
    };
  }

  /** Combine number and currency into an amount string. */
  function formatAmount(number: string, currency: string): string {
    if (!number) {
      return "";
    }
    return `${number} ${currency}`;
  }

  let parsed = $derived(parseAmount(posting.amount));

  function updateNumber(newNumber: string) {
    const newAmount = formatAmount(newNumber, parsed.currency);
    posting = posting.set("amount", newAmount);
  }

  function updateCurrency(newCurrency: string) {
    const newAmount = formatAmount(parsed.number, newCurrency);
    posting = posting.set("amount", newAmount);
  }

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
  <span class="amount-wrapper">
    <input
      type="number"
      class="amount-number"
      placeholder={_("Amount")}
      step="any"
      value={parsed.number}
      oninput={(e) => updateNumber(e.currentTarget.value)}
    />
    <select
      class="amount-currency"
      value={parsed.currency}
      onchange={(e) => updateCurrency(e.currentTarget.value)}
    >
      {#each $currencies as currency}
        <option value={currency}>{currency}</option>
      {/each}
      {#if !$currencies.includes(parsed.currency)}
        <option value={parsed.currency}>{parsed.currency}</option>
      {/if}
    </select>
  </span>
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

  .amount-wrapper {
    display: flex;
    flex: 1;
    gap: var(--flex-gap);
  }

  .amount-number {
    flex: 2;
    min-width: 80px;
  }

  .amount-currency {
    flex: 1;
    min-width: 70px;
  }

  @media (width <= 767px) {
    div {
      padding-left: 0;
    }

    .amount-wrapper {
      flex-basis: 100%;
    }
  }
</style>
