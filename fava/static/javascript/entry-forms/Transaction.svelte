<script context="module">
  const accountCompletionCache = {};
</script>

<script>
  import { tick } from "svelte";

  import { emptyPosting, Transaction } from "../entries";
  import { _, fetchAPI } from "../helpers";
  import { favaAPI } from "../stores";

  import AutocompleteInput from "../AutocompleteInput.svelte";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadata from "./EntryMetadata.svelte";
  import PostingSvelte from "./Posting.svelte";

  export let entry;
  let focusInput;
  let suggestions;
  let el;

  export function focus() {
    focusInput.focus();
  }

  function removePosting(posting) {
    entry.postings = entry.postings.filter(p => p !== posting);
  }

  async function addPosting() {
    entry.postings = entry.postings.concat(emptyPosting());
    await tick();
    const inputs = el.querySelectorAll(".posting .account input");
    inputs[inputs.length - 1].focus();
  }

  $: if (entry.payee) {
    const { payee } = entry;
    if (favaAPI.payees.includes(payee)) {
      if (!accountCompletionCache[payee]) {
        accountCompletionCache[payee] = fetchAPI("payee_accounts", { payee });
      }
      accountCompletionCache[payee].then(s => {
        suggestions = s;
      });
    }
  }

  // Autofill complete transactions.
  async function autocompleteSelectPayee() {
    if (entry.narration || !entry.postings.every(p => !p.account)) {
      return;
    }
    const data = await fetchAPI("payee_transaction", { payee: entry.payee });
    entry = Object.assign(new Transaction(), data, { date: entry.date });
  }

  function movePosting(ev) {
    const { from, to } = ev.detail;
    const moved = entry.postings[from];
    entry.postings.splice(from, 1);
    entry.postings.splice(to, 0, moved);
    entry.postings = entry.postings;
  }
</script>

<div class="entry-form transaction" bind:this={el}>
  <div class="fieldset">
    <input type="date" bind:value={entry.date} required />
    <input type="text" name="flag" bind:value={entry.flag} required />
    <label for="payee">{_('Payee')}:</label>
    <AutocompleteInput
      bind:this={focusInput}
      className="payee"
      placeholder={_('Payee')}
      bind:value={entry.payee}
      suggestions={favaAPI.payees}
      on:select={autocompleteSelectPayee} />
    <label for="payee">{_('Narration')}:</label>
    <input
      type="text"
      name="narration"
      placeholder={_('Narration')}
      bind:value={entry.narration} />
    <AddMetadataButton bind:meta={entry.meta} />
    <button
      class="muted round"
      type="button"
      on:click={addPosting}
      title={_('Add posting')}
      tabindex="-1">
      p
    </button>
  </div>
  <EntryMetadata bind:meta={entry.meta} />
  {#each entry.postings as posting, index}
    <PostingSvelte
      bind:posting
      {index}
      {suggestions}
      on:add={addPosting}
      on:move={movePosting}
      on:remove={() => removePosting(posting)} />
  {/each}
</div>
