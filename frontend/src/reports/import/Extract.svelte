<script lang="ts">
  import type { Entry as EntryType } from "../../entries";
  import { isDuplicate } from "../../entries";
  import Entry from "../../entry-forms/Entry.svelte";
  import { _ } from "../../i18n";
  import ModalBase from "../../modals/ModalBase.svelte";

  export let entries: EntryType[];
  export let save: () => void;
  export let close: () => void;

  let currentIndex = 0;

  $: shown = entries.length > 0;
  $: entry = entries[currentIndex];
  $: duplicate = entry && isDuplicate(entry);
  $: duplicates = entries.filter(isDuplicate).length;
  $: if (entries.length > 0 && currentIndex >= entries.length) {
    currentIndex = 0;
  }

  function submitOrNext() {
    if (currentIndex < entries.length - 1) {
      currentIndex += 1;
    } else {
      save();
    }
  }

  function previousEntry() {
    currentIndex = Math.max(currentIndex - 1, 0);
  }

  function toggleDuplicate() {
    if (entry) {
      entry.meta.__duplicate__ = !isDuplicate(entry);
    }
  }

  $: current_index_from_one = currentIndex + 1;
  $: total_without_duplicates = entries.length - duplicates;
</script>

<ModalBase {shown} closeHandler={close}>
  <form novalidate={duplicate} on:submit|preventDefault={submitOrNext}>
    <h3>{_("Import")}</h3>
    {#if entry}
      <div class="flex-row">
        <h3>
          Entry
          {current_index_from_one}
          of
          {entries.length}
          ({total_without_duplicates}
          to import):
        </h3>
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
      <div class="flex-row">
        {#if currentIndex > 0}
          <button
            type="button"
            class="muted"
            on:click={() => {
              currentIndex = 0;
            }}
          >
            ⏮
          </button>
          <button type="button" class="muted" on:click={previousEntry}>
            {_("Previous")}
          </button>
        {/if}
        <span class="spacer"></span>
        {#if currentIndex < entries.length - 1}
          <button type="submit">{_("Next")}</button>
          <button
            type="button"
            class="muted"
            on:click={() => {
              currentIndex = entries.length - 1;
            }}
          >
            ⏭
          </button>
        {:else}<button type="submit">{_("Save")}</button>{/if}
      </div>
      <hr />
      {#if entry.meta.__source__}
        <h3>
          {_("Source")}
          {#if entry.meta.lineno}({_("Line")}: {entry.meta.lineno}){/if}
        </h3>
        <pre>{entry.meta.__source__}</pre>
      {/if}
    {/if}
  </form>
</ModalBase>

<style>
  pre {
    font-size: 0.9em;
    white-space: pre-wrap;
  }

  .duplicate {
    opacity: 0.5;
  }
</style>
