<script lang="ts">
  import type { Entry } from "../../entries";
  import AccountInput from "../../entry-forms/AccountInput.svelte";
  import { _ } from "../../i18n";
  import type { ProcessedImportableFile } from ".";

  interface Props {
    files: ProcessedImportableFile[];
    extract_cache: Map<string, Entry[]>;
    file_accounts: Map<string, string>;
    file_names: Map<string, string>;
    selected: string | null;
    remove: (name: string) => void;
    move: (name: string, a: string, newName: string) => void;
    extract: (name: string, importer: string) => void;
  }

  let {
    files,
    extract_cache = $bindable(),
    file_accounts = $bindable(),
    file_names = $bindable(),
    selected = $bindable(),
    remove,
    move,
    extract,
  }: Props = $props();
</script>

{#each files as file (file.name)}
  <div class="header" title={file.name} class:selected={selected === file.name}>
    <button
      type="button"
      class="unset"
      onclick={() => {
        selected = selected === file.name ? null : file.name;
      }}
    >
      {file.basename}
    </button>
    <button
      type="button"
      class="round"
      onclick={() => {
        remove(file.name);
      }}
      title={_("Delete")}
      tabindex={-1}
    >
      ×
    </button>
  </div>
  {#each file.importers as info (info.importer_name)}
    {@const file_importer_key = `${file.name}:${info.importer_name}`}
    {@const account = file_accounts.get(file_importer_key) ?? info.account}
    {@const new_name = file_names.get(file_importer_key) ?? info.newName}
    <form
      class="flex-row"
      onsubmit={(event) => {
        event.preventDefault();
        move(file.name, account, new_name);
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
      {#if info.importer_name}
        {@const is_cached = extract_cache.has(file_importer_key)}
        <button
          type="button"
          title="{_('Extract')} with importer {info.importer_name}"
          onclick={() => {
            extract(file.name, info.importer_name);
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
{/each}

<style>
  .header {
    padding: 0.5rem;
    margin: 0.5rem 0;
    background-color: var(--summary-background);
  }

  .header button:first-child {
    width: 90%;
  }

  .header button:nth-child(2) {
    float: right;
  }

  .header.selected {
    background-color: var(--summary-background-darker);
  }
</style>
