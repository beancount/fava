<script>
  import { tick } from "svelte";

  import { Transaction, saveEntries } from "../entries";
  import { _ } from "../helpers";
  import { urlHash, closeOverlay } from "../stores";

  import TransactionComponent from "../entry-forms/Transaction.svelte";

  let entry = new Transaction();
  let transactionComponent;

  async function focus() {
    await tick();
    transactionComponent.focus();
  }

  async function submitAndNew(event) {
    if (event.target.form.reportValidity()) {
      await saveEntries([entry]);
      entry = new Transaction();
      focus();
    }
  }

  async function submit() {
    await saveEntries([entry]);
    entry = new Transaction();
    closeOverlay();
  }

  $: shown = $urlHash === "add-transaction";
  $: if (shown) focus();
</script>

<div class:shown class="overlay">
  <div class="overlay-background" on:click={closeOverlay} />
  <div class="overlay-content">
    <button type="button" class="muted close-overlay" on:click={closeOverlay}>
      x
    </button>
    <form on:submit|preventDefault={submit}>
      <h3>{_('New transaction')}:</h3>
      <TransactionComponent bind:this={transactionComponent} bind:entry />
      <div class="fieldset">
        <span class="spacer" />
        <button
          type="submit"
          on:click|preventDefault={submitAndNew}
          class="muted">
          {_('Save and add new')}
        </button>
        <button type="submit">{_('Save')}</button>
      </div>
    </form>
  </div>
</div>
