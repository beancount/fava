<script>
  import { tick } from "svelte";

  import e from "../events";
  import { Transaction, saveEntries } from "../entries";
  import { _, fetch, handleJSON } from "../helpers";
  import { urlHash, closeOverlay } from "../stores";

  import TransactionComponent from "../entry-forms/Transaction.svelte";

  let entry = new Transaction();
  let transactionComponent;

  $: shown = $urlHash === "add-transaction";
  $: if (shown) focus();

  async function focus() {
    await tick();
    transactionComponent.focus();
  }

  async function submitAndNew() {
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
</script>
<div class:shown class="overlay">
  <div class="overlay-background" on:click="{closeOverlay}"></div>
  <div class="overlay-content">
    <button type="button" class="muted close-overlay" on:click="{closeOverlay}">
      x
    </button>
    <form on:submit|preventDefault="{submit}">
      <h3>{_('New transaction')}:</h3>
      <TransactionComponent
        bind:this="{transactionComponent}"
        bind:entry="{entry}"
      />
      <div class="fieldset">
        <span class="spacer"></span>
        <button
          type="submit"
          on:click|preventDefault="{submitAndNew}"
          class="muted"
        >
          {_('Save and add new')}
        </button>
        <button type="submit">{_('Save')}</button>
      </div>
    </form>
  </div>
</div>
