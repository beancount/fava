<script>
  import { createEventDispatcher } from "svelte";
  import { _ } from "../i18n";

  import AccountInput from "../entry-forms/AccountInput.svelte";

  /** @type {import("./helpers").ProcessedImportableFiles} */
  export let files;

  /** @type {Map<string,import('../entries').Entry[]>} */
  export let extractCache;

  /** @type {string|null} */
  export let selected;

  const dispatch = createEventDispatcher();

  /** @param {string} filename */
  function remove(filename) {
    dispatch("removeFile", filename);
  }

  /** @param {import('./helpers').MoveFileArgs} args */
  function move(args) {
    dispatch("moveFile", args);
  }

  /** @param {import('./helpers').ExtractFileArgs} args */
  function extract(args) {
    dispatch("extractFile", args);
  }
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
      on:click={() => remove(file.name)}
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
        on:click={() =>
          move({
            filename: file.name,
            account: info.account,
            newName: info.newName,
          })}
      >
        {"Move"}
      </button>
      {#if info.importer_name}
        <button
          type="button"
          title="{_('Extract')} with importer {info.importer_name}"
          on:click={() =>
            extract({ filename: file.name, importer: info.importer_name })}
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
      {:else}{_("No importer matched this file.")}{/if}
    </div>
  {/each}
{/each}

<style>
  .header {
    padding: 0.5rem;
    margin: 0.5rem 0;
    cursor: pointer;
    background-color: var(--color-table-header-background);
  }
  .header button {
    float: right;
  }
</style>
