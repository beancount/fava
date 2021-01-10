<script>
  import { onMount } from "svelte";
  import { get, saveEntries, moveDocument, deleteDocument } from "../api";
  import { _ } from "../i18n";
  import router from "../router";

  import { preprocessData, isDuplicate } from "./helpers";

  import Extract from "./Extract.svelte";
  import AccountInput from "../entry-forms/AccountInput.svelte";
  import { notify } from "../notifications";
  import DocumentPreview from "../documents/DocumentPreview.svelte";

  /** @type {import("./helpers").ImportableFiles} */
  export let data;

  /** @type {import('../entries').Entry[]} */
  let entries = [];

  /** @type {string | null} */
  let selected = null;

  /** @type {import("./helpers").ProcessedImportableFiles} */
  let preprocessedData = [];

  /** @type {Map<string,import('../entries').Entry[]>} */
  let extractCache = new Map();

  function preventNavigation() {
    return extractCache.size > 0
      ? "There are unfinished imports, are you sure you want to continue?"
      : null;
  }

  onMount(() => {
    preprocessedData = preprocessData(data);
    router.interruptHandlers.add(preventNavigation);

    return () => {
      router.interruptHandlers.delete(preventNavigation);
    };
  });

  /**
   * Move the given file to the new file name (and remove from the list).
   * @param {string} filename
   * @param {string} account
   * @param {string} newName
   */
  async function move(filename, account, newName) {
    const moved = await moveDocument(filename, account, newName);
    if (moved) {
      preprocessedData = preprocessedData.filter(
        (item) => item.name !== filename
      );
    }
  }

  /**
   * Delete the given file and remove it from the displayed list.
   * @param {string} filename
   */
  async function remove(filename) {
    const removed = await deleteDocument(filename);
    if (removed) {
      preprocessedData = preprocessedData.filter(
        (item) => item.name !== filename
      );
    }
  }

  /**
   * Open the extract dialog for the given file/importer combination.
   * @param {string} filename
   * @param {string} importer
   */
  async function extract(filename, importer) {
    const extractCacheKey = `${filename}:${importer}`;
    let cached = extractCache.get(extractCacheKey);
    if (!cached) {
      cached = await get("extract", { filename, importer });
      if (!cached.length) {
        notify("No entries to import from this file.", "warning");
        return;
      }
      extractCache.set(extractCacheKey, cached);
      extractCache = extractCache;
    }
    entries = cached;
  }

  /**
   * Save the current entries.
   */
  async function save() {
    const withoutDuplicates = entries.filter((e) => !isDuplicate(e));
    const key = [...extractCache].find(([, e]) => e === entries)?.[0];
    if (key) {
      extractCache.delete(key);
      extractCache = extractCache;
    }
    entries = [];
    await saveEntries(withoutDuplicates);
  }
</script>

<Extract
  {entries}
  on:close={() => {
    entries = [];
  }}
  on:save={save}
/>
<div class="fixed-fullsize-container">
  <div class="filelist">
    {#each preprocessedData as file}
      <div
        class="header"
        title={file.name}
        on:click|self={() => {
          selected = selected === file.name ? null : file.name;
        }}
      >
        {file.basename}
        <button
          class="round"
          on:click={() => remove(file.name)}
          type="button"
          title={_("Delete")}
          tabindex={-1}> × </button>
      </div>
      {#each file.importers as info}
        <div class="flex-row">
          <AccountInput bind:value={info.account} />
          <input size={40} bind:value={info.newName} />
          <button
            type="button"
            on:click={() => move(file.name, info.account, info.newName)}>
            {"Move"}
          </button>
          {#if info.importer_name}
            <button
              type="button"
              title="{_('Extract')} with importer {info.importer_name}"
              on:click={() => extract(file.name, info.importer_name)}>
              {extractCache.get(`${file.name}:${info.importer_name}`)
                ? _("Continue")
                : _("Extract")}
            </button>
            {#if extractCache.get(`${file.name}:${info.importer_name}`)}
              <button
                type="button"
                on:click={() => {
                  extractCache.delete(`${file.name}:${info.importer_name}`);
                  extractCache = extractCache;
                }}>
                {_("Clear")}
              </button>
            {/if}
            {info.importer_name}
          {:else}{_("No importer matched this file.")}{/if}
        </div>
      {/each}
    {/each}
  </div>
  {#if selected}
    <div>
      <DocumentPreview filename={selected} />
    </div>
  {/if}
</div>

<style>
  .header {
    padding: 0.5rem;
    margin: 0.5rem 0;
    cursor: pointer;
    background-color: var(--color-table-header-background);
  }
  .header button {
    float: right;
  }
  .fixed-fullsize-container {
    display: flex;
    align-items: stretch;
  }
  .fixed-fullsize-container > * {
    flex: 1 1 40%;
    overflow: auto;
  }
  .filelist {
    padding: 1rem;
  }
</style>
