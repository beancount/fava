<script>
  import { Balance, Note, Transaction } from "../entries";
  import { saveEntries } from "../api";
  import { _ } from "../helpers";
  import { urlHash, closeOverlay } from "../stores";

  import ModalBase from "./ModalBase.svelte";
  import BalanceComponent from "../entry-forms/Balance.svelte";
  import NoteComponent from "../entry-forms/Note.svelte";
  import TransactionComponent from "../entry-forms/Transaction.svelte";

  const entryTypes = [
    [_("Transaction"), Transaction],
    [_("Balance"), Balance],
    [_("Note"), Note],
  ];
  let entry = new Transaction();

  $: svelteComponent = {
    Balance: BalanceComponent,
    Note: NoteComponent,
    Transaction: TransactionComponent,
  }[entry.type];

  async function submitAndNew(event) {
    if (event.target.form.reportValidity()) {
      await saveEntries([entry]);
      entry = new entry.constructor();
    }
  }

  async function submit() {
    await saveEntries([entry]);
    entry = new entry.constructor();
    closeOverlay();
  }

  $: shown = $urlHash === "add-transaction";
</script>

<ModalBase {shown}>
  <form on:submit|preventDefault={submit}>
    <h3>
      {_('Add')}
      {#each entryTypes as [name, Cls]}
        <button
          type="button"
          class:muted={entry.type !== Cls.name}
          on:click={() => {
            entry = new Cls();
          }}>
          {name}
        </button>
        {' '}
      {/each}
    </h3>
    <svelte:component this={svelteComponent} bind:entry />
    <div class="flex-row">
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
</ModalBase>
