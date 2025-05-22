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
  let entry: Transaction | Balance | Note = $state.raw(
    Transaction.empty(todayAsString()),
  );

  async function submit(event: SubmitEvent) {
    event.preventDefault();
    await saveEntries([entry]);
    const added_entry_date = entry.date;
    // Reuse the date of the entry that was just added.
    // @ts-expect-error all these entries have that static method, but TS is not able to determine that
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
    entry = entry.constructor.empty(added_entry_date);
    if (!$addEntryContinue) {
      closeOverlay();
    }
  }

  let shown = $derived($urlHash === "add-transaction");
</script>

<ModalBase {shown} focus=".payee input">
  <form onsubmit={submit}>
    <h3>
      {_("Add")}
      {#each entryTypes as [Cls, displayName] (displayName)}
        <button
          type="button"
          class:muted={!(entry instanceof Cls)}
          onclick={() => {
            // when switching between entry types, keep the date.
            entry = Cls.empty(entry.date);
          }}
        >
          {displayName}
        </button>
        <!-- eslint-disable-next-line svelte/no-useless-mustaches -->
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
