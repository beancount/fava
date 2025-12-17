<script lang="ts">
  import {
    get_narration_transaction,
    get_narrations,
    get_payee_accounts,
    get_payee_transaction,
  } from "../api/index.ts";
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import type { EntryMetadata, Transaction } from "../entries/index.ts";
  import { Posting } from "../entries/index.ts";
  import { _ } from "../i18n.ts";
  import { move } from "../lib/array.ts";
  import { notify_err } from "../notifications.ts";
  import { payees } from "../stores/index.ts";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadataSvelte from "./EntryMetadata.svelte";
  import PostingSvelte from "./Posting.svelte";

  interface Props {
    entry: Transaction;
  }

  let { entry = $bindable() }: Props = $props();
  let suggestions: string[] | undefined = $state.raw();

  let payee = $derived(entry.payee);
  $effect(() => {
    if (payee) {
      suggestions = undefined;
      if ($payees.includes(payee)) {
        get_payee_accounts({ payee })
          .then((s) => {
            suggestions = s;
          })
          .catch((error: unknown) => {
            notify_err(
              error,
              (err) =>
                `Fetching account suggestions for payee ${payee} failed: ${err.message}`,
            );
          });
      }
    }
  });

  let narration = $derived(entry.get_narration_tags_links());
  let narration_suggestions: string[] = $state.raw([]);
  $effect(() => {
    get_narrations()
      .then((s) => {
        narration_suggestions = s;
      })
      .catch((error: unknown) => {
        notify_err(
          error,
          (err) => `Fetching narration suggestions failed: ${err.message}`,
        );
      });
  });

  // Autofill complete transactions.
  async function autocompleteSelectPayee() {
    if (entry.narration || entry.postings.some((p) => !p.is_empty())) {
      return;
    }
    const payee_transaction = await get_payee_transaction({
      payee: entry.payee,
    });
    entry = payee_transaction.set("date", entry.date);
  }
  async function autocompleteSelectNarration() {
    if (entry.payee || entry.postings.some((p) => !p.is_empty())) {
      return;
    }
    const data = await get_narration_transaction({ narration });
    data.set("date", entry.date);
    entry = data;
    narration = entry.get_narration_tags_links();
  }

  // Always have one empty posting at the end.
  $effect(() => {
    if (!entry.postings.some((p) => p.is_empty())) {
      entry = entry.set("postings", entry.postings.concat(Posting.empty()));
    }
  });
</script>

<div class="flex-column">
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
        onSelect={autocompleteSelectPayee}
        --autocomplete-wrapper-flex="1"
      />
    </label>
    <label class="narration">
      <span class="hide-on-desktop">{_("Narration")}:</span>
      <AutocompleteInput
        placeholder={_("Narration")}
        bind:value={narration}
        suggestions={narration_suggestions}
        onSelect={autocompleteSelectNarration}
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
  {#each entry.postings, index (index)}
    <!-- Using the indexed access (instead of `as posting` in the each) seems to track
         the reactivity differently and avoids cursor jumping on the posting inputs. -->
    {@const posting = entry.postings[index]}
    {#if posting}
      <PostingSvelte
        bind:posting={
          () => posting,
          (posting: Posting) => {
            entry = entry.set("postings", entry.postings.with(index, posting));
          }
        }
        {index}
        {suggestions}
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
</div>

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
