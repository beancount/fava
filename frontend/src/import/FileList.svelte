<script lang="ts">
  import type { Entry } from "../entries";
  import AccountInput from "../entry-forms/AccountInput.svelte";
  import { _ } from "../i18n";

  import type { ProcessedImportableFiles } from "./helpers";

  export let files: ProcessedImportableFiles;
  export let extractCache: Map<string, Entry[]>;
  export let selected: string | null;
  export let removeFile: (name: string) => unknown;
  export let moveFile: (name: string, a: string, newName: string) => unknown;
  export let extract: (name: string, importer: string) => unknown;
</script>

{#each files as file}
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
      on:click={() => removeFile(file.name)}
      type="button"
      title={_("Delete")}
      tabindex={-1}
    >
      ×
    </button>
  </div>
  {#each file.importers as info}
    <div class="flex-row">
      <AccountInput bind:value={info.account} />
      <input size={40} bind:value={info.newName} />
      <button
        type="button"
        on:click={() => moveFile(file.name, info.account, info.newName)}
      >
        {"Move"}
      </button>
      {#if info.importer_name}
        <button
          type="button"
          title="{_('Extract')} with importer {info.importer_name}"
          on:click={() => extract(file.name, info.importer_name)}
        >
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
            }}
          >
            {_("Clear")}
          </button>
        {/if}
        {info.importer_name}
      {/if}
    </div>
  {/each}
{/each}

<style>
  .header {
    padding: 0.5rem;
    margin: 0.5rem 0;
    cursor: pointer;
    background-color: var(--color-sidebar-background);
  }
  .header button {
    float: right;
  }
</style>
