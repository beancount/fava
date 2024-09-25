<script lang="ts" context="module">
  const TAGS_RE = /(?:^|\s)#([A-Za-z0-9\-_/.]+)/g;
  const LINKS_RE = /(?:^|\s)\^([A-Za-z0-9\-_/.]+)/g;
</script>

<script lang="ts">
  import { get } from "../api";
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import type { Transaction } from "../entries";
  import { Posting } from "../entries";
  import { _ } from "../i18n";
  import { notify_err } from "../notifications";
  import { payees } from "../stores";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadata from "./EntryMetadata.svelte";
  import PostingSvelte from "./Posting.svelte";

  export let entry: Transaction;
  let suggestions: string[] | undefined;

  function removePosting(posting: Posting) {
    entry.postings = entry.postings.filter((p) => p !== posting);
  }

  $: payee = entry.payee;
  $: if (payee) {
    suggestions = undefined;
    if ($payees.includes(payee)) {
      get("payee_accounts", { payee })
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

  /// Extract tags and links that can be provided in the narration <input>.
  function onNarrationChange({
    currentTarget,
  }: {
    currentTarget: HTMLInputElement;
  }) {
    const { value } = currentTarget;
    entry.tags = [...value.matchAll(TAGS_RE)].map((a) => a[1] ?? "");
    entry.links = [...value.matchAll(LINKS_RE)].map((a) => a[1] ?? "");
    entry.narration = value
      .replaceAll(TAGS_RE, "")
      .replaceAll(LINKS_RE, "")
      .trim();
  }

  /// Output tags and links in the narration <input>
  function combineNarrationTagsLinks(e: Transaction): string {
    let val = e.narration;
    if (e.tags.length) {
      val += ` ${e.tags.map((t) => `#${t}`).join(" ")}`;
    }
    if (e.links.length) {
      val += ` ${e.links.map((t) => `^${t}`).join(" ")}`;
    }
    return val;
  }
  $: narration = combineNarrationTagsLinks(entry);

  // Autofill complete transactions.
  async function autocompleteSelectPayee() {
    if (entry.narration || !entry.postings.every((p) => !p.account)) {
      return;
    }
    const data = await get("payee_transaction", { payee: entry.payee });
    data.date = entry.date;
    entry = data;
  }

  function movePosting({ from, to }: { from: number; to: number }) {
    const moved = entry.postings[from];
    if (moved) {
      entry.postings.splice(from, 1);
      entry.postings.splice(to, 0, moved);
      entry.postings = entry.postings;
    }
  }

  // Always have one empty posting at the end.
  $: if (!entry.postings.some((p) => p.is_empty())) {
    entry.postings = entry.postings.concat(new Posting());
  }
</script>

<div>
  <div class="flex-row">
    <input type="date" bind:value={entry.date} required />
    <input type="text" name="flag" bind:value={entry.flag} required />
    <!-- svelte-ignore a11y-label-has-associated-control -->
    <label>
      <span>{_("Payee")}:</span>
      <AutocompleteInput
        className="payee"
        placeholder={_("Payee")}
        bind:value={entry.payee}
        suggestions={$payees}
        on:select={autocompleteSelectPayee}
      />
    </label>
    <label>
      <span>{_("Narration")}:</span>
      <input
        type="text"
        name="narration"
        placeholder={_("Narration")}
        value={narration}
        on:change={onNarrationChange}
      />
      <AddMetadataButton bind:meta={entry.meta} />
    </label>
  </div>
  <EntryMetadata bind:meta={entry.meta} />
  <div class="flex-row">
    <span class="label"> <span>{_("Postings")}:</span> </span>
  </div>
  {#each entry.postings as posting, index}
    <PostingSvelte
      bind:posting
      {index}
      {suggestions}
      date={entry.date}
      move={movePosting}
      remove={() => {
        removePosting(posting);
      }}
    />
  {/each}
</div>

<style>
  input[name="flag"] {
    width: 1.5em;
    padding-right: 2px;
    padding-left: 2px;
    text-align: center;
  }

  div :global(.payee) {
    flex-grow: 1;
    flex-basis: 100px;
  }

  input[name="narration"] {
    flex-grow: 1;
    flex-basis: 200px;
  }

  label > span:first-child,
  .label > span:first-child {
    display: none;
  }

  @media (width <= 767px) {
    label > span:first-child,
    .label > span:first-child {
      display: initial;
      width: 100%;
    }
  }
</style>
