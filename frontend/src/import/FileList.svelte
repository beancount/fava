<script>
  import { _ } from "../i18n";

  import AccountInput from "../entry-forms/AccountInput.svelte";

  /** @type {import("./helpers").ProcessedImportableFiles} */
  export let files;

  /** @type {Map<string,import('../entries').Entry[]>} */
  export let extractCache;

  /** @type {string|null} */
  export let selected;

  /** @type {(name: string) => void} */
  export let removeFile;

  /** @type {(name: string, account: string, newName: string) => void} */
  export let moveFile;

  /** @type {(name: string, importer: string) => void} */
  export let extract;
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
