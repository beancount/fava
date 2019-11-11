<script>
  import { tick } from "svelte";

  import { Balance, Transaction, saveEntries } from "../entries";
  import { _ } from "../helpers";
  import { urlHash, closeOverlay } from "../stores";

  import ModalBase from "./ModalBase.svelte";
  import TransactionComponent from "../entry-forms/Transaction.svelte";
  import BalanceComponent from "../entry-forms/Balance.svelte";

  const entryTypes = [
    [_("Transaction"), Transaction],
    [_("Balance"), Balance],
  ];
  let entry = new Transaction();

  $: svelteComponent = {
    Transaction: TransactionComponent,
    Balance: BalanceComponent,
  }[entry.constructor.name];

  let entryComponent;

  async function focus() {
    await tick();
    if (entryComponent.focus) entryComponent.focus();
  }

  async function submitAndNew(event) {
    if (event.target.form.reportValidity()) {
      await saveEntries([entry]);
      entry = new entry.constructor();
      focus();
    }
  }

  async function submit() {
    await saveEntries([entry]);
    entry = new entry.constructor();
    closeOverlay();
  }

  $: shown = $urlHash === "add-transaction";
  $: if (shown) focus();
</script>

<ModalBase {shown}>
  <form on:submit|preventDefault={submit}>
    <h3>
      {_('Add')}
      {#each entryTypes as [name, Cls, component]}
        <button
          type="button"
          class:muted={!(entry instanceof Cls)}
          on:click={() => {
            entry = new Cls();
          }}>
          {name}
        </button>
      {/each}
    </h3>
    <svelte:component
      this={svelteComponent}
      bind:this={entryComponent}
      bind:entry />
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
</ModalBase>
