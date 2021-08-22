<script lang="ts">
  import { saveEntries } from "../api";
  import { create } from "../entries";
  import type { EntryTypeName } from "../entries";
  import Entry from "../entry-forms/Entry.svelte";
  import { _ } from "../i18n";
  import { closeOverlay, urlHash } from "../stores";

  import ModalBase from "./ModalBase.svelte";

  const entryTypes: [EntryTypeName, string][] = [
    ["Transaction", _("Transaction")],
    ["Balance", _("Balance")],
    ["Note", _("Note")],
  ];

  let entry = create("Transaction");

  async function submitAndNew({
    currentTarget,
  }: {
    currentTarget: HTMLButtonElement;
  }) {
    if (currentTarget.form?.reportValidity()) {
      await saveEntries([entry]);
      entry = create(entry.type);
    }
  }

  async function submit() {
    await saveEntries([entry]);
    entry = create(entry.type);
    closeOverlay();
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
            entry = create(type);
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
      <button
        type="submit"
        on:click|preventDefault={submitAndNew}
        class="muted"
      >
        {_("Save and add new")}
      </button>
      <button type="submit">{_("Save")}</button>
    </div>
  </form>
</ModalBase>
