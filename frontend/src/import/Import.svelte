<script>
  import { onMount } from "svelte";
  import { todayAsString } from "../format";
  import { _, urlFor } from "../helpers";
  import { moveDocument, deleteDocument } from "../api";

  import { newFilename, extractURL } from "./helpers";

  import Extract from "./Extract.svelte";
  import AccountInput from "../entry-forms/AccountInput.svelte";

  export let data;
  let preprocessedData = [];

  const today = todayAsString();

  // Initially set the file names for all importable files.
  function preprocessData(arr) {
    return arr.map((file) => {
      const importers = file.importers.map((importerfile) => ({
        ...importerfile,
        newName: newFilename(importerfile.date, importerfile.name),
      }));
      if (importers.length === 0) {
        const newName = newFilename(today, file.basename);
        importers.push({ account: "", newName });
      }
      return {
        ...file,
        importers,
      };
    });
  }

  onMount(() => {
    preprocessedData = preprocessData(data);
  });

  async function move(filename, account, newName) {
    const moved = await moveDocument(filename, account, newName);
    if (moved) {
      preprocessedData = preprocessedData.filter(
        (item) => item.name !== filename
      );
    }
  }
  async function remove(filename) {
    const removed = await deleteDocument(filename);
    if (removed) {
      preprocessedData = preprocessedData.filter(
        (item) => item.name !== filename
      );
    }
  }
</script>

<style>
  .header {
    padding: 0.5rem;
    margin: 0.5rem 0;
    background-color: var(--color-table-header-background);
  }
  .header button {
    float: right;
  }
  .button {
    padding: 4px 8px;
  }
</style>

<Extract />
{#each preprocessedData as file}
  <div class="header" title={file.name}>
    <a
      href={urlFor('document', { filename: file.name })}
      data-remote
      target="_blank">
      {file.basename}
    </a>
    <button
      class="round"
      on:click={() => remove(file.name)}
      type="button"
      title={_('Delete')}
      tabindex="-1">
      ×
    </button>
  </div>
  {#each file.importers as info}
    <div class="flex-row">
      <AccountInput bind:value={info.account} />
      <input size="40" bind:value={info.newName} />
      <button
        type="button"
        on:click={() => move(file.name, info.account, info.newName)}>
        {'Move'}
      </button>
      {#if info.importer_name}
        <a
          class="button"
          title="{_('Extract')} with importer {info.importer_name}"
          href={extractURL(file.name, info.importer_name)}>
          {_('Extract')}
        </a>
        {info.importer_name}
      {:else}{_('No importer matched this file.')}{/if}
    </div>
  {/each}
{/each}
