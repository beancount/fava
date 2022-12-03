<script lang="ts">
  import { onMount } from "svelte";

  import { deleteDocument, get, moveDocument, saveEntries } from "../../api";
  import type { Entry } from "../../entries";
  import { isDuplicate } from "../../entries";
  import { urlFor } from "../../helpers";
  import { _ } from "../../i18n";
  import { notify } from "../../notifications";
  import router from "../../router";
  import { fava_options } from "../../stores";
  import DocumentPreview from "../documents/DocumentPreview.svelte";

  import Extract from "./Extract.svelte";
  import FileList from "./FileList.svelte";
  import type { PageData, ProcessedImportableFile } from "./load";

  export let data: PageData;

  /** The array of entries to show the modal for. */
  let entries: Entry[] = [];

  /** Name of the currently selected file. */
  let selected: string | null = null;

  /** All files (importable and those without importers). */
  let files: ProcessedImportableFile[] = [];

  let extractCache = new Map<string, Entry[]>();

  $: importableFiles = files.filter(
    (i) => i.importers[0]?.importer_name !== ""
  );
  $: otherFiles = files.filter((i) => i.importers[0]?.importer_name === "");

  const preventNavigation = () =>
    extractCache.size > 0
      ? "There are unfinished imports, are you sure you want to continue?"
      : null;

  onMount(() => router.addInteruptHandler(preventNavigation));
  onMount(() => {
    files = data;
  });

  /**
   * Move the given file to the new file name (and remove from the list).
   */
  async function move(filename: string, account: string, newName: string) {
    const moved = await moveDocument(filename, account, newName);
    if (moved) {
      files = files.filter((item) => item.name !== filename);
    }
  }

  /**
   * Delete the given file and remove it from the displayed list.
   */
  async function remove(filename: string) {
    // eslint-disable-next-line no-alert
    if (!window.confirm(_("Delete this file?"))) {
      return;
    }
    const removed = await deleteDocument(filename);
    if (removed) {
      files = files.filter((item) => item.name !== filename);
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

{#if !$fava_options.import_config}
  <p>
    No importers configured. See <a href={urlFor("help/import")}
      >Help (Import)</a
    > for more information.
  </p>
{:else}
  <Extract
    {entries}
    close={() => {
      entries = [];
    }}
    {save}
  />
  <div class="fixed-fullsize-container">
    <div class="filelist">
      {#if files.length === 0}
        <p>{_("No files were found for import.")}</p>
      {/if}
      {#if importableFiles.length > 0}
        <div>
          <h2>{_("Importable Files")}</h2>
          <FileList
            files={importableFiles}
            {extractCache}
            bind:selected
            {move}
            {remove}
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
            {move}
            {remove}
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
{/if}

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

  hr {
    margin: 1rem 0;
  }
</style>
