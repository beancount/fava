<script lang="ts">
  import { saveEntries } from "../api";
  import { create } from "../entries";
  import type { EntryTypeName } from "../entries";
  import Entry from "../entry-forms/Entry.svelte";
  import { todayAsString } from "../format";
  import { _ } from "../i18n";
  import { closeOverlay, urlHash } from "../stores";
  import { addEntryContinue } from "../stores/editor";

  import ModalBase from "./ModalBase.svelte";

  const entryTypes: [EntryTypeName, string][] = [
    ["Transaction", _("Transaction")],
    ["Balance", _("Balance")],
    ["Note", _("Note")],
  ];

  // For the first entry to be added, use today as the default date.
  let entry = create("Transaction", todayAsString());

  async function submit() {
    await saveEntries([entry]);
    const added_entry_date = entry.date;
    // Reuse the date of the entry that was just added.
    entry = create(entry.type, added_entry_date);
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
      {#each entryTypes as [type, displayName]}
        <button
          type="button"
          class:muted={entry.type !== type}
          on:click={() => {
            // when switching between entry types, keep the date.
            entry = create(type, entry.date);
          }}
        >
          {displayName}
        </button>
        {" "}
      {/each}
    </h3>
    <Entry bind:entry />
    <div class="flex-row">
      <span class="spacer" />
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
