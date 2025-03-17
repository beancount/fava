<script lang="ts">
  import type { Entry as EntryType } from "../../entries";
  import Entry from "../../entry-forms/Entry.svelte";
  import { _ } from "../../i18n";
  import ModalBase from "../../modals/ModalBase.svelte";

  interface Props {
    entries: EntryType[];
    save: () => void;
    close: () => void;
  }

  let { entries = $bindable(), save, close }: Props = $props();

  let currentIndex = $state.raw(0);
  let count = $derived(entries.length);
  let shown = $derived(count > 0);

  let entry = $derived(entries[currentIndex]);
  let duplicate = $derived(entry?.is_duplicate());
  let count_duplicates = $derived(
    entries.filter((e) => e.is_duplicate()).length,
  );
  $effect(() => {
    if (count > 0 && currentIndex >= count) {
      currentIndex = 0;
    }
  });

  function submitOrNext(event: SubmitEvent) {
    event.preventDefault();
    if (currentIndex < count - 1) {
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
      entries[currentIndex] = entry.set_meta(
        "__duplicate__",
        !entry.is_duplicate(),
      );
    }
  }

  let current_index_from_one = $derived(currentIndex + 1);
  let count_without_duplicates = $derived(count - count_duplicates);
</script>

<ModalBase {shown} closeHandler={close}>
  <form novalidate={duplicate} onsubmit={submitOrNext}>
    <h3>{_("Import")}</h3>
    {#if entry}
      <div class="flex-row">
        <h3>
          Entry
          {current_index_from_one}
          of
          {count}
          ({count_without_duplicates}
          to import):
        </h3>
        <span class="spacer"></span>
        <label class="button muted">
          <input
            type="checkbox"
            checked={duplicate}
            onclick={toggleDuplicate}
          />
          {_("ignore duplicate")}
        </label>
      </div>
      <div class:duplicate>
        <Entry
          bind:entry={
            () => entry,
            (entry: EntryType) => {
              entries[currentIndex] = entry;
            }
          }
        />
      </div>
      <div class="flex-row">
        {#if currentIndex > 0}
          <button
            type="button"
            class="muted"
            onclick={() => {
              currentIndex = 0;
            }}
          >
            ⏮
          </button>
          <button type="button" class="muted" onclick={previousEntry}>
            {_("Previous")}
          </button>
        {/if}
        <span class="spacer"></span>
        {#if currentIndex < entries.length - 1}
          <button type="submit">{_("Next")}</button>
          <button
            type="button"
            class="muted"
            onclick={() => {
              currentIndex = entries.length - 1;
            }}
          >
            ⏭
          </button>
        {:else}<button type="submit">{_("Save")}</button>{/if}
      </div>
      <hr />
      {#if entry.meta.get("__source__")}
        <h3>
          {_("Source")}
          {#if entry.meta.lineno}({_("Line")}: {entry.meta.lineno}){/if}
        </h3>
        <pre>{entry.meta.get("__source__")}</pre>
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
