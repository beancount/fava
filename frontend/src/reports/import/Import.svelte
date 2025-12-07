<script lang="ts">
  import { onMount } from "svelte";
  import { SvelteMap } from "svelte/reactivity";

  import {
    delete_document,
    get_extract,
    move_document,
    save_entries,
  } from "../../api/index.ts";
  import type { Entry } from "../../entries/index.ts";
  import { urlFor } from "../../helpers.ts";
  import { _ } from "../../i18n.ts";
  import { is_non_empty } from "../../lib/array.ts";
  import { notify, notify_err } from "../../notifications.ts";
  import { router } from "../../router.ts";
  import { import_config } from "../../stores/fava_options.ts";
  import DocumentPreview from "../documents/DocumentPreview.svelte";
  import Extract from "./Extract.svelte";
  import FileList from "./FileList.svelte";
  import ImportFileUpload from "./ImportFileUpload.svelte";
  import type { ImportReportProps } from "./index.ts";

  let { files }: ImportReportProps = $props();

  // initially show the other files if no importable files are present
  // svelte-ignore state_referenced_locally
  const show_other_files_initially = files.every(
    (file) => !file.identified_by_importers,
  );

  /** Whether the `<details>` for the "other files" is open. */
  let show_other_files = $state.raw(show_other_files_initially);

  /** The array of entries to show the modal for. */
  let entries: Entry[] = $state([]);

  /** Name of the currently selected file. */
  let selected: string | null = $state.raw(null);

  /** The lists of entries for file and importer combos where extract was started and not completed. */
  let extract_cache = new SvelteMap<string, Entry[]>();
  /** The account names chosen for a file and importer. */
  let file_accounts = new SvelteMap<string, string>();
  /** The names chosen for a file and importer. */
  let file_names = new SvelteMap<string, string>();

  /** Importable files. */
  let importable_files = $derived(
    files.filter((file) => file.identified_by_importers),
  );
  /** Files not identified by any importer. */
  let other_files = $derived(
    files.filter((file) => !file.identified_by_importers),
  );

  const preventNavigation = () =>
    extract_cache.size > 0
      ? "There are unfinished imports, are you sure you want to continue?"
      : null;

  onMount(() => router.add_interrupt_handler(preventNavigation));

  /**
   * Move the given file to the new file name (and remove from the list).
   */
  async function move(filename: string, account: string, newName: string) {
    const moved = await move_document(filename, account, newName);
    if (moved) {
      router.reload();
    }
  }

  /**
   * Delete the given file and remove it from the displayed list.
   */
  async function remove(filename: string) {
    if (!window.confirm(_("Delete this file?"))) {
      return;
    }
    const removed = await delete_document(filename);
    if (removed) {
      if (selected === filename) {
        selected = null;
      }
      router.reload();
    }
  }

  /**
   * Open the extract dialog for the given file/importer combination.
   */
  async function extract(filename: string, importer: string) {
    const file_importer_key = `${filename}:${importer}`;
    const cached = extract_cache.get(file_importer_key);
    if (cached) {
      entries = cached;
      return;
    }
    try {
      entries = await get_extract({ filename, importer });
      if (entries.length) {
        extract_cache.set(file_importer_key, entries);
      } else {
        notify("No entries to import from this file.", "warning");
      }
    } catch (error) {
      notify_err(error);
    }
  }

  /**
   * Save the current entries.
   */
  async function save() {
    const without_duplicates = entries.filter((e) => !e.is_duplicate());
    const key = [...extract_cache].find(([, e]) => e === entries)?.[0];
    if (key != null) {
      extract_cache.delete(key);
    }
    entries = [];
    if (is_non_empty(without_duplicates)) {
      await save_entries(without_duplicates);
    }
  }
</script>

{#if $import_config == null}
  <p>
    No importers configured. See <a href={$urlFor("help/import")}
      >Help (Import)</a
    > for more information.
  </p>
{:else}
  <Extract
    bind:entries
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
      {#if importable_files.length > 0}
        <div>
          <h2>{_("Importable Files")}</h2>
          <FileList
            files={importable_files}
            {extract_cache}
            {file_accounts}
            {file_names}
            bind:selected
            {move}
            {remove}
            {extract}
          />
        </div>
        <hr />
      {/if}
      {#if other_files.length > 0}
        <details bind:open={show_other_files}>
          <summary>{_("Non-importable Files")}</summary>
          <FileList
            files={other_files}
            {extract_cache}
            {file_accounts}
            {file_names}
            bind:selected
            {move}
            {remove}
            {extract}
          />
        </details>
      {/if}
      <ImportFileUpload />
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
