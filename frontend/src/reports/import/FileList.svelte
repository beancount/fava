<script lang="ts">
  import type { Entry } from "../../entries";
  import AccountInput from "../../entry-forms/AccountInput.svelte";
  import { _ } from "../../i18n";
  import type { ProcessedImportableFile } from ".";

  export let files: ProcessedImportableFile[];
  export let extractCache: Map<string, Entry[]>;
  export let selected: string | null;
  export let remove: (name: string) => unknown;
  export let move: (name: string, a: string, newName: string) => unknown;
  export let extract: (name: string, importer: string) => unknown;
</script>

{#each files as file}
  <div class="header" title={file.name} class:selected={selected === file.name}>
    <button
      type="button"
      class="unset"
      on:click={() => {
        selected = selected === file.name ? null : file.name;
      }}>{file.basename}</button
    >
    <button
      type="button"
      class="round"
      on:click={() => remove(file.name)}
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
        on:click={() => move(file.name, info.account, info.newName)}
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
