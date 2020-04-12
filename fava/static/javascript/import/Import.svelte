<script>
  import { onMount } from "svelte";
  import { todayAsString } from "../format";
  import { _, urlFor } from "../helpers";
  import { moveDocument } from "../api";

  import { newFilename, extractURL } from "./helpers";

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
</script>

<style>
  .flex-row {
    display: flex;
  }
  .button {
    padding: 4px 8px;
  }
</style>

{#each preprocessedData as file}
  <pre title={file.name}>
    <a
      href={urlFor('document', { filename: file.name })}
      data-remote
      target="_blank">
      {file.basename}
    </a>
  </pre>
  {#each file.importers as info}
    <p class="flex-row">
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
    </p>
  {/each}
{/each}
