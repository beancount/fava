<script lang="ts">
  import { saveEntries } from "../api";
  import { Balance, Note, Transaction } from "../entries";
  import Entry from "../entry-forms/Entry.svelte";
  import { todayAsString } from "../format";
  import { _ } from "../i18n";
  import { addEntryContinue } from "../stores/editor";
  import { closeOverlay, urlHash } from "../stores/url";
  import ModalBase from "./ModalBase.svelte";

  /** The entry types which have support adding in the modal. */
  const entryTypes = [
    [Transaction, _("Transaction")],
    [Balance, _("Balance")],
    [Note, _("Note")],
  ] as const;

  // For the first entry to be added, use today as the default date.
  let entry: Transaction | Balance | Note = new Transaction(todayAsString());

  async function submit() {
    await saveEntries([entry]);
    const added_entry_date = entry.date;
    // Reuse the date of the entry that was just added.
    // @ts-expect-error entry.constructor is only typed as "Function" but the
    //                  new is required here to avoid a runtime error.
    // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-assignment
    entry = new entry.constructor(added_entry_date);
    if (!$addEntryContinue) {
      closeOverlay();
    }
  }

  $: shown = $urlHash === "add-transaction";
</script>

<ModalBase {shown} focus=".payee input">
  <form on:submit|preventDefault={submit}>
    <h3>
      {_("Add")}
      {#each entryTypes as [Cls, displayName]}
        <button
          type="button"
          class:muted={!(entry instanceof Cls)}
          on:click={() => {
            // when switching between entry types, keep the date.
            entry = new Cls(entry.date);
          }}
        >
          {displayName}
        </button>
        {" "}
      {/each}
    </h3>
    <Entry bind:entry />
    <div class="flex-row">
      <span class="spacer"></span>
      <label>
        <input type="checkbox" bind:checked={$addEntryContinue} />
        <span>{_("continue")}</span>
      </label>
      <button type="submit">{_("Save")}</button>
    </div>
  </form>
</ModalBase>

<style>
  label span {
    margin-right: 1rem;
  }
</style>
