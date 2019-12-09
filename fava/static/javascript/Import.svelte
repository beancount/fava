<script>
  import { todayAsString } from "./format";
  import { _ } from "./helpers";
  import { moveDocument } from "./api";

  import AccountInput from "./entry-forms/AccountInput.svelte";

  export let data;

  const today = todayAsString();

  /**
   * Construct the filename from date and basename.
   */
  function newFilename(date, basename) {
    if (/^\d{4}-\d{2}-\d{2}/.test(basename)) {
      return basename;
    }
    return `${date} ${basename}`;
  }

  // Initially set the file names for all importable files.
  $: for (const items of Object.values(data)) {
    for (const item of items) {
      item.newName = item.newName || newFilename(today, item.basename);
      for (const importInfo of item.importers) {
        importInfo.newName =
          importInfo.newName || newFilename(importInfo.date, importInfo.name);
      }
    }
  }

  function extractURL(filename, importer) {
    const params = new URLSearchParams();
    params.set("filename", filename);
    params.set("importer", importer);
    return `#extract-${params.toString()}`;
  }

  function documentURL(filename) {
    const params = new URLSearchParams();
    params.set("filename", filename);
    return `../document/?${params.toString()}`;
  }

  async function move(filename, account, newName) {
    const moved = await moveDocument(filename, account, newName);
    if (moved) {
      for (const [directory, items] of Object.entries(data)) {
        data[directory] = items.filter(item => item.name !== filename);
      }
    }
  }
</script>

<style>
  .flex-row {
    display: flex;
  }
  .button {
    padding: 4px 8px;
  }
</style>

{#each Object.entries(data) as [directory, items]}
  <h3>Directory: {directory}</h3>
  {#each items as item}
    <pre title={item.name}>
      <a href={documentURL(item.name)} data-remote target="_blank">
        {item.basename}
      </a>
    </pre>
    {#if item.importers.length}
      {#each item.importers as info}
        <p class="flex-row">
          <AccountInput bind:value={info.account} />
          <input size="40" bind:value={info.newName} />
          <button
            type="button"
            on:click={() => move(item.name, info.account, info.newName)}>
            {'Move'}
          </button>
          <a
            class="button"
            title="{_('Extract')} with importer {info.importer_name}"
            href={extractURL(item.name, info.importer_name)}>
            {_('Extract')} ( {info.importer_name} )
          </a>
        </p>
      {/each}
    {:else}
      <p>
        <AccountInput bind:value={item.account} />
        <input size="40" bind:value={item.newName} />
        <button
          type="button"
          on:click={() => move(item.name, item.account, item.newName)}>
          {'Move'}
        </button>
      </p>
    {/if}
  {/each}
{/each}
