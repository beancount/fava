<script lang="ts">
  import { onMount } from "svelte";

  import { deleteDocument, get, moveDocument, saveEntries } from "../api";
  import DocumentPreview from "../documents/DocumentPreview.svelte";
  import type { Entry } from "../entries";
  import { _ } from "../i18n";
  import { notify } from "../notifications";
  import router from "../router";

  import Extract from "./Extract.svelte";
  import FileList from "./FileList.svelte";
  import { isDuplicate, preprocessData } from "./helpers";
  import type { ImportableFiles, ProcessedImportableFiles } from "./helpers";

  export let data: ImportableFiles;

  let entries: Entry[] = [];
  let selected: string | null = null;

  let preprocessedData: ProcessedImportableFiles = [];

  let extractCache = new Map<string, Entry[]>();

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
   */
  async function move(filename: string, account: string, newName: string) {
    const moved = await moveDocument(filename, account, newName);
    if (moved) {
      preprocessedData = preprocessedData.filter(
        (item) => item.name !== filename
      );
    }
  }

  /**
   * Delete the given file and remove it from the displayed list.
   */
  async function remove(filename: string) {
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
   */
  async function extract(filename: string, importer: string) {
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
