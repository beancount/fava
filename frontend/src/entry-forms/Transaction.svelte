<script>
  import { emptyPosting, Transaction } from "../entries";
  import { get } from "../api";
  import { _ } from "../i18n";
  import { payees } from "../stores";

  import AutocompleteInput from "../AutocompleteInput.svelte";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadata from "./EntryMetadata.svelte";
  import PostingSvelte from "./Posting.svelte";

  /** @type {import("../entries").Transaction} */
  export let entry;
  /** @type {string[] | undefined} */
  let suggestions;

  /**
   * @param {import("../entries").Posting} posting
   */
  function removePosting(posting) {
    entry.postings = entry.postings.filter((p) => p !== posting);
  }

  function addPosting() {
    entry.postings = entry.postings.concat(emptyPosting());
  }

  $: payee = entry.payee;
  $: if (payee) {
    suggestions = undefined;
    if ($payees.includes(payee)) {
      get("payee_accounts", { payee }).then((s) => {
        suggestions = s;
      });
    }
  }

  // Autofill complete transactions.
  async function autocompleteSelectPayee() {
    if (entry.narration || !entry.postings.every((p) => !p.account)) {
      return;
    }
    const data = await get("payee_transaction", { payee: entry.payee });
    entry = Object.assign(new Transaction(), data, { date: entry.date });
  }

  /**
   * @param {{from: number, to: number}} arg
   */
  function movePosting({ from, to }) {
    const moved = entry.postings[from];
    entry.postings.splice(from, 1);
    entry.postings.splice(to, 0, moved);
    entry.postings = entry.postings;
  }
</script>

<!-- svelte-ignore a11y-label-has-associated-control -->
<div>
  <div class="flex-row">
    <input type="date" bind:value={entry.date} required />
    <input type="text" name="flag" bind:value={entry.flag} required />
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
        bind:value={entry.narration}
      />
      <AddMetadataButton bind:meta={entry.meta} />
    </label>
    <button
      class="muted round"
      type="button"
      on:click={addPosting}
      title={_("Add posting")}
      tabindex={-1}
    >
      p
    </button>
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
      add={addPosting}
      move={movePosting}
      remove={() => removePosting(posting)}
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
    flex-basis: 100px;
    flex-grow: 1;
  }

  input[name="narration"] {
    flex-basis: 200px;
    flex-grow: 1;
  }

  label > span:first-child,
  .label > span:first-child {
    display: none;
  }

  @media (max-width: 767px) {
    label > span:first-child,
    .label > span:first-child {
      display: initial;
      width: 100%;
    }
  }
</style>
