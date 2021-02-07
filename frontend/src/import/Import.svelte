<script>
  import { onMount } from "svelte";
  import { get, saveEntries, moveDocument, deleteDocument } from "../api";
  import { _ } from "../i18n";
  import router from "../router";

  import { preprocessData, isDuplicate } from "./helpers";

  import Extract from "./Extract.svelte";
  import FileList from "./FileList.svelte";
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

  $: importableFiles = preprocessedData.filter(
    (i) => i.importers[0].importer_name !== ""
  );
  $: otherFiles = preprocessedData.filter(
    (i) => i.importers[0].importer_name === ""
  );

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
    // eslint-disable-next-line
    if (!confirm(_("Delete this file?"))) {
      return;
    }
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
  close={() => {
    entries = [];
  }}
  {save}
/>
<div class="fixed-fullsize-container">
  <div class="filelist">
    {#if preprocessedData.length === 0}
      <p>{_("No files were found for import.")}</p>
    {/if}
    {#if importableFiles.length > 0}
      <div class="importable-files">
        <h2>{_("Importable Files")}</h2>
        <FileList
          files={importableFiles}
          {extractCache}
          bind:selected
          moveFile={move}
          removeFile={remove}
          {extract}
        />
      </div>
      <hr />
    {/if}
    {#if otherFiles.length > 0}
      <details open={importableFiles.length === 0}>
        <summary>{_("Non-importable Files")}</summary>
        <FileList
          files={otherFiles}
          {extractCache}
          bind:selected
          moveFile={move}
          removeFile={remove}
          {extract}
        />
      </details>
    {/if}
  </div>
  {#if selected}
    <div>
      <DocumentPreview filename={selected} />
    </div>
  {/if}
</div>

<style>
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
  .importable-files {
    padding-bottom: 0.8rem;
  }
</style>
