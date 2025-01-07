<script lang="ts">
  // This is very similar to the Extract.svelte component in the traditional importer.
  import type { Entry as EntryType } from "../../entries";
  import { isDuplicate, Transaction } from "../../entries";
  import Entry from "../../entry-forms/Entry.svelte";
  import { _ } from "../../i18n";
  import ModalBase from "../../modals/ModalBase.svelte";

  export let entry: EntryType | undefined;
  export let close: () => void;
  $: shown = !!entry; // Truthiness check (if entry is undefined then shown === false)

  $: duplicate = entry && isDuplicate(entry);

  function toggleDuplicate() {
    if (entry) {
      entry.meta.__duplicate__ = !isDuplicate(entry);
    }
  }

  function cleanup_and_close() {
    if (entry instanceof Transaction) {
      // The editor can add an extra posting to allow for editing. Clean it up
      // before closing.
      entry.postings = entry.postings.filter((p) => !p.is_empty());
    }
    close();
  }
</script>

<ModalBase {shown} closeHandler={cleanup_and_close}>
  <form novalidate={duplicate} on:submit|preventDefault={() => {}}>
    <h3>{_("Import")}</h3>
    {#if entry}
      <div class="flex-row">
        <h3>{_("Edit Entry")}</h3>
        <span class="spacer"></span>
        <label class="button muted">
          <input
            type="checkbox"
            checked={duplicate}
            on:click={toggleDuplicate}
          />
          ignore duplicate
        </label>
      </div>
      <div class:duplicate>
        <Entry bind:entry />
      </div>
    {/if}
  </form>
</ModalBase>

<style>
  .duplicate {
    opacity: 0.5;
  }
</style>
