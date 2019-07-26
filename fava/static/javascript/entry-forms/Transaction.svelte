<script context="module">
  const accountCompletionCache = {};
</script>

<script>
  import { tick } from "svelte";

  import { Posting } from "../entries";
  import { _, fetchAPI } from "../helpers";
  import { favaAPI } from "../stores";

  import AutocompleteInput from "../AutocompleteInput.svelte";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadata from "./EntryMetadata.svelte";
  import AccountInput from "./AccountInput.svelte";

  export let entry;
  let focusInput;
  let suggestions;
  let postingRow;

  export function focus() {
    focusInput.focus();
  }

  function removePosting(posting) {
    entry.postings = entry.postings.filter(p => p !== posting);
  }

  async function addPosting() {
    entry.postings = entry.postings.concat(new Posting());
    await tick();
    postingRow.querySelector("input").focus();
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
  function autocompleteSelectPayee() {
    if (entry.narration || !entry.postings.every(p => !p.account)) return;
    fetchAPI("payee_transaction", { payee: entry.payee }).then(data => {
      entry = Object.assign(data, { date: entry.date });
    });
  }
</script>

<div class="entry-form transaction">
  <div class="fieldset">
    <input type="date" bind:value={entry.date} required />
    <input type="text" name="flag" bind:value={entry.flag} required />
    <label for="payee">{_('Payee')}:</label>
    <AutocompleteInput
      bind:this={focusInput}
      name="payee"
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
  <div class="postings">
    {#each entry.postings as posting}
      <div class="fieldset posting" bind:this={postingRow}>
        <button
          class="muted round remove-fieldset"
          on:click={() => removePosting(posting)}
          type="button"
          tabindex="-1">
          ×
        </button>
        <AccountInput bind:value={posting.account} {suggestions} />
        <input
          type="text"
          class="amount"
          placeholder={_('Amount')}
          bind:value={posting.amount} />
        <button
          class="muted round add-row"
          type="button"
          on:click={addPosting}
          title={_('Add posting')}>
          +
        </button>
      </div>
    {/each}
  </div>
</div>
