<script lang="ts">
  import { SvelteMap } from "svelte/reactivity";

  import { get_extract, save_entries } from "../../api/index.ts";
  import type { Entry } from "../../entries/index.ts";
  import { urlFor } from "../../helpers.ts";
  import { _ } from "../../i18n.ts";
  import { is_non_empty } from "../../lib/array.ts";
  import { log_error } from "../../log.ts";
  import { notify, notify_err } from "../../notifications.ts";
  import { loading_state, router, set_query_param } from "../../router.ts";
  import { import_config } from "../../stores/fava_options.ts";
  import { searchParams } from "../../stores/url.ts";
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
  let entries = $state<Entry[]>([]);

  /** Name of the currently selected file. */
  let selected = $state.raw<string>();

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

  let has_unfinished_imports = $derived(extract_cache.size > 0);
  $effect(() =>
    has_unfinished_imports
      ? router.add_interrupt_handler(({ current, target }) =>
          // On reload or query changes, the component state is kept
          target?.pathname !== current.pathname
            ? "There are unfinished imports, are you sure you want to continue?"
            : null,
        )
      : undefined,
  );

  // Clear selection if file is removed.
  $effect(() => {
    if (!files.some(({ name }) => name === selected)) {
      selected = undefined;
    }
  });

  const extract_filename = $derived($searchParams.get("extract_filename"));
  const extract_importer = $derived($searchParams.get("extract_importer"));

  /** Load the entries to extract for given file and importer. */
  async function load_extract(filename: string, importer: string) {
    try {
      entries = await loading_state.await(get_extract({ filename, importer }));
      if (entries.length) {
        extract_cache.set(`${filename}:${importer}`, entries);
      } else {
        notify("No entries to import from this file.", "warning");
      }
    } catch (error) {
      notify_err(error);
    }
  }

  // Load the entries to extract if the URL parameters are set.
  $effect(() => {
    if (extract_filename != null && extract_importer != null) {
      const cached = extract_cache.get(
        `${extract_filename}:${extract_importer}`,
      );
      if (cached) {
        entries = cached;
      } else {
        load_extract(extract_filename, extract_importer).catch(log_error);
      }
    } else {
      entries = [];
    }
  });

  /**
   * Open the extract dialog for the given file/importer combination.
   */
  function extract(filename: string, importer: string) {
    const target = new URL(router.current);
    set_query_param(target, "extract_filename", filename);
    set_query_param(target, "extract_importer", importer);
    router.navigate(target, false);
  }

  /** Close the extract dialog. */
  function close_extract() {
    extract("", "");
  }

  /**
   * Save the current entries.
   */
  async function save() {
    const without_duplicates = entries.filter((e) => !e.is_duplicate());
    if (extract_filename != null && extract_importer != null) {
      extract_cache.delete(`${extract_filename}:${extract_importer}`);
    }
    close_extract();
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
  <Extract bind:entries close={close_extract} {save} />
  <div class="fixed-fullsize-container">
    <div class="filelist flex-column">
      {#if files.length === 0}
        <p>{_("No files were found for import.")}</p>
      {/if}
      {#if importable_files.length > 0}
        <h2>{_("Importable Files")}</h2>
        <FileList
          files={importable_files}
          {extract_cache}
          {file_accounts}
          {file_names}
          bind:selected
          {extract}
        />
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

    > * {
      flex: 1 1 40%;
      overflow: auto;
    }
  }

  .filelist {
    padding: 1rem;
  }
</style>
