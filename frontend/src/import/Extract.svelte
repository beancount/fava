<script>
  import { get, saveEntries } from "../api";
  import { _ } from "../i18n";
  import { urlHash, closeOverlay } from "../stores";

  import ModalBase from "../modals/ModalBase.svelte";
  import Entry from "../entry-forms/Entry.svelte";

  /** @type {import('../entries').Entry[]} */
  let entries = [];
  /** @type {number} */
  let currentIndex = 0;
  /** @type {boolean} */
  let duplicate;
  /** @type {number} */
  let duplicates;

  /** @type {import('../entries').Entry} */
  let entry;
  /** @type {boolean} */
  let shown;

  /**
   * @param {import("../entries").Entry} e
   */
  function isDuplicate(e) {
    return !!e.meta.__duplicate__;
  }

  $: shown = $urlHash.startsWith("extract");
  $: if (shown) {
    const params = new URLSearchParams($urlHash.slice(8));
    const filename = params.get("filename") || "";
    const importer = params.get("importer") || "";
    get("extract", { filename, importer }).then((data) => {
      entries = data;
    });
  }
  $: entry = entries[currentIndex];
  $: if (entry) {
    duplicates = entry && entries.filter((e) => isDuplicate(e)).length;
    duplicate = isDuplicate(entry);
  }

  async function submitOrNext() {
    if (currentIndex < entries.length - 1) {
      currentIndex += 1;
    } else {
      await saveEntries(entries.filter((e) => !isDuplicate(e)));
      closeOverlay();
    }
  }

  function previousEntry() {
    currentIndex = Math.max(currentIndex - 1, 0);
  }

  function toggleDuplicate() {
    entry.meta.__duplicate__ = !entry.meta.__duplicate__;
  }
</script>

<style>
  pre {
    font-size: 0.9em;
    white-space: pre-wrap;
  }

  .duplicate {
    opacity: 0.5;
  }
</style>

<ModalBase {shown}>
  <form novalidate={duplicate} on:submit|preventDefault={submitOrNext}>
    <h3>{_('Import')}</h3>
    {#if entry}
      <div class="flex-row">
        <h3>
          Entry {currentIndex + 1} of {entries.length} ({entries.length - duplicates}
          to import):
        </h3>
        <span class="spacer" />
        <label class="button muted">
          <input
            type="checkbox"
            checked={duplicate}
            on:click={toggleDuplicate} />
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
            }}>
            ⏮
          </button>
          <button type="button" class="muted" on:click={previousEntry}>
            {_('Previous')}
          </button>
        {/if}
        <span class="spacer" />
        {#if currentIndex < entries.length - 1}
          <button type="submit">{_('Next')}</button>
          <button
            type="button"
            class="muted"
            on:click={() => {
              currentIndex = entries.length - 1;
            }}>
            ⏭
          </button>
        {:else}
          <button type="submit">{_('Save')}</button>
        {/if}
      </div>
      <hr />
      {#if entry.meta.__source__}
        <h3>
          {_('Source')}
          {#if entry.meta.lineno}({_('Line')}: {entry.meta.lineno}){/if}
        </h3>
        <pre>{entry.meta.__source__}</pre>
      {/if}
    {/if}
  </form>
</ModalBase>
