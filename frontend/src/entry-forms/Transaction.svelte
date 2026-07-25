<script lang="ts">
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import {
    get_narration_transaction,
    get_payee_transaction,
  } from "../api/index.ts";
  import type { EntryMetadata, Transaction } from "../entries/index.ts";
  import { Posting } from "../entries/index.ts";
  import { _ } from "../i18n.ts";
  import { move } from "../lib/array.ts";
  import { payees } from "../stores/index.ts";
  import { ledger_mtime } from "../stores/mtime.ts";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadataSvelte from "./EntryMetadata.svelte";
  import PostingSvelte from "./Posting.svelte";
  import {
    fetch_narrations,
    fetch_payee_accounts,
  } from "./suggestions.svelte.ts";

  interface Props {
    entry: Transaction;
  }

  let { entry = $bindable() }: Props = $props();

  let payee = $derived(entry.payee);
  let narration = $derived(entry.get_narration_tags_links());

  // Autofill complete transactions.
  async function autocomplete_select_payee() {
    if (entry.narration || entry.postings.some((p) => !p.is_empty())) {
      return;
    }
    const transaction = await get_payee_transaction({ payee });
    entry = transaction.set("date", entry.date);
  }
  async function autocomplete_select_narration() {
    if (entry.payee || entry.postings.some((p) => !p.is_empty())) {
      return;
    }
    const transaction = await get_narration_transaction({ narration });
    entry = transaction.set("date", entry.date);
  }

  // Always have one empty posting at the end.
  $effect(() => {
    if (!entry.postings.some((p) => p.is_empty())) {
      entry = entry.set("postings", entry.postings.concat(Posting.empty()));
    }
  });
</script>

<div class="flex-row">
  <input
    type="date"
    bind:value={
      () => entry.date,
      (date: string) => {
        entry = entry.set("date", date);
      }
    }
    required
  />
  <input
    type="text"
    name="flag"
    bind:value={
      () => entry.flag,
      (flag: string) => {
        entry = entry.set("flag", flag);
      }
    }
    required
  />
  <label>
    <span class="hide-on-desktop">{_("Payee")}:</span>
    <AutocompleteInput
      placeholder={_("Payee")}
      bind:value={
        () => entry.payee,
        (payee: string) => {
          entry = entry.set("payee", payee);
        }
      }
      suggestions={$payees}
      onSelect={autocomplete_select_payee}
      --autocomplete-wrapper-flex="1"
    />
  </label>
  <label class="narration">
    <span class="hide-on-desktop">{_("Narration")}:</span>
    <AutocompleteInput
      placeholder={_("Narration")}
      bind:value={narration}
      suggestions={fetch_narrations($ledger_mtime).data}
      onSelect={autocomplete_select_narration}
      onEnter={() => {
        entry = entry.set_narration_tags_links(narration);
      }}
      onBlur={() => {
        entry = entry.set_narration_tags_links(narration);
      }}
      --autocomplete-wrapper-flex="2"
    />
    <AddMetadataButton
      bind:meta={
        () => entry.meta,
        (meta: EntryMetadata) => {
          entry = entry.set("meta", meta);
        }
      }
    />
  </label>
</div>
<EntryMetadataSvelte
  bind:meta={
    () => entry.meta,
    (meta: EntryMetadata) => {
      entry = entry.set("meta", meta);
    }
  }
/>
<div class="flex-row hide-on-desktop">
  <span class="label">{_("Postings")}:</span>
</div>
{#each entry.postings, index}
  <!-- Using the indexed access (instead of `as posting` in the each) seems to track
         the reactivity differently and avoids cursor jumping on the posting inputs. -->
  {@const posting = entry.postings[index]}
  {#if posting != null}
    <PostingSvelte
      bind:posting={
        () => posting,
        (posting: Posting) => {
          entry = entry.set("postings", entry.postings.with(index, posting));
        }
      }
      {index}
      suggestions={$payees.includes(payee)
        ? fetch_payee_accounts($ledger_mtime, payee).data
        : undefined}
      date={entry.date}
      move={({ from, to }: { from: number; to: number }) => {
        entry = entry.set("postings", move(entry.postings, from, to));
      }}
      remove={() => {
        entry = entry.set("postings", entry.postings.toSpliced(index, 1));
      }}
    />
  {/if}
{/each}

<style>
  input[name="flag"] {
    width: 1.5em;
    padding-right: 2px;
    padding-left: 2px;
    text-align: center;
  }

  .hide-on-desktop {
    display: none;
  }

  @media (width <= 767px) {
    .hide-on-desktop {
      display: initial;
      width: 100%;
    }
  }
</style>
