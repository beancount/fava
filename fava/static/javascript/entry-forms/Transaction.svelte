<script>
  import { tick } from "svelte";

  import { Posting } from "../entries";
  import { _, fetch, handleJSON } from "../helpers";

  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadata from "./EntryMetadata.svelte";
  import AccountInput from "./AccountInput.svelte";

  export let entry;
  let focusInput;
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

  // Autofill complete transactions.
  function autocompleteSelectPayee(event) {
    entry.payee = event.target.value;
    if (entry.narration || !entry.postings.every(p => !p.account)) return;
    const params = new URLSearchParams();
    params.set("payee", entry.payee);
    fetch(
      `${window.favaAPI.baseURL}api/payee-transaction/?${params.toString()}`
    )
      .then(handleJSON)
      .then(data => {
        entry = Object.assign(data.payload, { date: entry.date });
      });
  }
</script>
<div class="entry-form transaction">
  <div class="fieldset">
    <input type="date" bind:value="{entry.date}" required />
    <input type="text" name="flag" bind:value="{entry.flag}" required />
    <label for="payee">{_('Payee')}:</label>
    <input
      type="text"
      name="payee"
      placeholder="{_('Payee')}"
      list="payees"
      bind:this="{focusInput}"
      bind:value="{entry.payee}"
      on:autocomplete-select="{autocompleteSelectPayee}"
    />
    <label for="payee">{_('Narration')}:</label>
    <input
      type="text"
      name="narration"
      placeholder="{_('Narration')}"
      bind:value="{entry.narration}"
    />
    <AddMetadataButton bind:meta="{entry.meta}" />
    <button
      class="muted round"
      type="button"
      on:click="{addPosting}"
      title="{_('Add posting')}"
      tabindex="-1"
    >
      p
    </button>
  </div>
  <EntryMetadata bind:meta="{entry.meta}" />
  <div class="postings">
    {#each entry.postings as posting }
    <div class="fieldset posting" bind:this="{postingRow}">
      <button
        class="muted round remove-fieldset"
        on:click="{() => removePosting(posting)}"
        type="button"
        tabindex="-1"
      >
        ×
      </button>
      <AccountInput bind:value="{posting.account}" />
      <input
        type="text"
        class="amount"
        placeholder="{_('Amount')}"
        bind:value="{posting.amount}"
      />
      <button
        class="muted round add-row"
        type="button"
        on:click="{addPosting}"
        title="{_('Add posting')}"
      >
        +
      </button>
    </div>
    {/each}
  </div>
</div>
