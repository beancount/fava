<script lang="ts">
  import {
    Balance,
    isDuplicate,
    Transaction,
    type Entry as EntryType,
  } from "../../entries";
  import { _ } from "../../i18n";

  export let entry: EntryType;
  export let manual_edit: () => void;
  $: duplicate = isDuplicate(entry);
</script>

{#if entry instanceof Transaction}
  <li class={{ transaction: true, duplicate: duplicate }}>
    <p>
      <span class="select"></span>
      <span class="datecell">{entry.date}</span>
      <span class="flag">*</span>
      <span class="description"
        ><strong class="payee">{entry.payee || ""}</strong
        >{#if entry.payee && entry.narration}<span class="separator"
          ></span>{/if}{entry.narration || ""}</span
      >
      <span class="amount"></span>
      <span class="edit"
        ><button class="muted" on:click={manual_edit}>⋮</button></span
      >
    </p>
    <ul class="postings">
      {#each entry.postings as posting}
        <li>
          <p>
            <span class="select"></span>
            <span class="datecell"></span>
            <span class="flag"></span>
            <span class="description">{posting.account}</span>
            <span class="amount">{posting.amount}</span>
            <span class="edit"></span>
          </p>
        </li>
      {/each}
    </ul>
  </li>
{:else if entry instanceof Balance}
  <li class={{ balance: true, duplicate: duplicate }}>
    <p>
      <span class="select"></span>
      <span class="datecell">{entry.date}</span>
      <span class="flag">Bal</span>
      <span class="description">{entry.account}</span>
      <span class="amount">{entry.amount.number} {entry.amount.currency}</span>
      <span class="edit"><button on:click={manual_edit}>⋮</button></span>
    </p>
  </li>
{/if}

<style>
</style>
