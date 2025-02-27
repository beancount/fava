<script lang="ts">
  import { SimpleTransaction } from ".";
  import { _ } from "../../i18n";
  import { isDuplicate } from "../../entries";
  import { slide } from "svelte/transition";

  export let entry: SimpleTransaction;
  export let selected = false;
  export let manual_edit: () => void;
  $: transaction = entry.transaction;
  $: duplicate = isDuplicate(transaction);
</script>

<li class="transaction" transition:slide|global>
  <label class={{ duplicate: duplicate, selected: selected }}>
    <p>
      <span class="select"
        ><input type="checkbox" bind:checked={selected} /></span
      >
      <span class="datecell">{transaction.date}</span>
      <span class="flag">*</span>
      <span class="description"
        ><strong class="payee">{transaction.payee || ""}</strong
        >{#if transaction.payee && transaction.narration}<span class="separator"
          ></span>{/if}{transaction.narration || ""}</span
      >
      <span class="num">{entry.getAmount()}</span>
      <span class="edit"><button on:click={manual_edit}>⋮</button></span>
    </p>
  </label>
</li>

<style>
  label.selected p {
    background-color: var(--background-darker);
  }
</style>
