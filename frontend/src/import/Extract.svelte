<script>
  import { createEventDispatcher } from "svelte";
  import { _ } from "../i18n";

  import ModalBase from "../modals/ModalBase.svelte";
  import Entry from "../entry-forms/Entry.svelte";
  import { isDuplicate } from "./helpers";

  /** @type {import('../entries').Entry[]} */
  export let entries;

  let currentIndex = 0;

  $: shown = entries.length > 0;
  $: entry = entries[currentIndex];
  $: duplicate /** @type {boolean} */ = entry && isDuplicate(entry);
  $: duplicates = entries.filter((e) => isDuplicate(e)).length;
  $: if (entries.length > 0 && currentIndex >= entries.length) {
    currentIndex = 0;
  }

  const dispatch = createEventDispatcher();

  const closeHandler = () => dispatch("close");

  async function submitOrNext() {
    if (currentIndex < entries.length - 1) {
      currentIndex += 1;
    } else {
      dispatch("save");
    }
  }

  function previousEntry() {
    currentIndex = Math.max(currentIndex - 1, 0);
  }

  function toggleDuplicate() {
    entry.meta.__duplicate__ = !entry.meta.__duplicate__;
  }
</script>

<ModalBase {shown} {closeHandler}>
  <form novalidate={duplicate} on:submit|preventDefault={submitOrNext}>
    <h3>{_("Import")}</h3>
    {#if entry}
      <div class="flex-row">
        <h3>
          Entry
          {currentIndex + 1}
          of
          {entries.length}
          ({entries.length - duplicates}
          to import):
        </h3>
        <span class="spacer" />
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
            }}> ⏮ </button>
          <button type="button" class="muted" on:click={previousEntry}>
            {_("Previous")}
          </button>
        {/if}
        <span class="spacer" />
        {#if currentIndex < entries.length - 1}
          <button type="submit">{_("Next")}</button>
          <button
            type="button"
            class="muted"
            on:click={() => {
              currentIndex = entries.length - 1;
            }}> ⏭ </button>
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
