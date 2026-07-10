<script lang="ts">
  import type { SvelteMap } from "svelte/reactivity";

  import { delete_document, move_document } from "../../api/index.ts";
  import type { Entry } from "../../entries/index.ts";
  import AccountInput from "../../entry-forms/AccountInput.svelte";
  import { _ } from "../../i18n.ts";
  import { log_error } from "../../log.ts";
  import { router } from "../../router.ts";
  import type { ProcessedImportableFile } from "./index.ts";

  interface Props {
    files: ProcessedImportableFile[];
    extract_cache: SvelteMap<string, Entry[]>;
    file_accounts: SvelteMap<string, string>;
    file_names: SvelteMap<string, string>;
    selected: string | undefined;
    extract: (name: string, importer: string) => void;
  }

  let {
    files,
    extract_cache = $bindable(),
    file_accounts = $bindable(),
    file_names = $bindable(),
    selected = $bindable(),
    extract,
  }: Props = $props();

  /**
   * Move the given file to the new file name (and reload to remove from the list).
   */
  async function move(filename: string, account: string, new_name: string) {
    const moved = await move_document(filename, account, new_name);
    if (moved) {
      router.reload();
    }
  }

  /**
   * Delete the given file and reload to remove it from the displayed list.
   */
  async function remove(filename: string) {
    if (!window.confirm(_("Delete this file?"))) {
      return;
    }
    const removed = await delete_document(filename);
    if (removed) {
      router.reload();
    }
  }
</script>

{#each files as file (file.name)}
  <div class="header" title={file.name} class:selected={selected === file.name}>
    <button
      type="button"
      class="unset"
      onclick={() => {
        selected = selected === file.name ? undefined : file.name;
      }}
    >
      {file.basename}
    </button>
    <button
      type="button"
      class="round"
      onclick={() => {
        remove(file.name).catch(log_error);
      }}
      title={_("Delete")}
      tabindex={-1}
    >
      ×
    </button>
  </div>
  <div class="flex-column">
    {#each file.importers as info (info.importer_name)}
      {@const file_importer_key = `${file.name}:${info.importer_name ?? ""}`}
      {@const account = file_accounts.get(file_importer_key) ?? info.account}
      {@const new_name = file_names.get(file_importer_key) ?? info.new_name}
      <form
        class="flex-row"
        onsubmit={(event) => {
          event.preventDefault();
          move(file.name, account, new_name).catch(log_error);
        }}
      >
        <AccountInput
          bind:value={
            () => account,
            (value: string) => {
              file_accounts.set(file_importer_key, value);
            }
          }
          required
        />
        <input
          size={40}
          bind:value={
            () => new_name,
            (value: string) => {
              file_names.set(file_importer_key, value);
            }
          }
        />
        <button type="submit">
          {_("Move")}
        </button>
        {#if info.importer_name != null}
          {@const is_cached = extract_cache.has(file_importer_key)}
          <button
            type="button"
            title="{_('Extract')} with importer {info.importer_name}"
            onclick={() => {
              if (info.importer_name != null) {
                extract(file.name, info.importer_name);
              }
            }}
          >
            {is_cached ? _("Continue") : _("Extract")}
          </button>
          {#if is_cached}
            <button
              type="button"
              onclick={() => {
                extract_cache.delete(file_importer_key);
              }}
            >
              {_("Clear")}
            </button>
          {/if}
          {info.importer_name}
        {/if}
      </form>
    {/each}
  </div>
{/each}

<style>
  .header {
    padding: 0.5rem;
    background-color: var(--summary-background);

    button:first-child {
      width: 90%;
    }

    button:nth-child(2) {
      float: right;
    }

    &.selected {
      background-color: var(--summary-background-darker);
    }
  }
</style>
