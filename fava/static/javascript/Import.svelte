<script>
  import { onMount } from "svelte";
  import { _, fetchAPI } from "./helpers";
  import { notify } from "./notifications";

  import AccountInput from "./entry-forms/AccountInput.svelte";

  export let data;
  const today = new Date().toISOString().slice(0, 10);
  $: for (const items of Object.values(data)) {
    for (const item of items) {
      item.newName = `${today} ${item.basename}`;
      for (const importInfo of item.importers) {
        importInfo.newName = `${importInfo.date} ${importInfo.name}`;
      }
    }
  }

  function extractURL(filename, importer) {
    const params = new URLSearchParams();
    params.set("filename", filename);
    params.set("importer", importer);
    return `#extract-${params.toString()}`;
  }

  function move(filename, account, newName) {
    const options = {
      filename,
      account,
      newName,
    };
    fetchAPI("move", options)
      .then(notify)
      .catch(error => {
        notify(error, "error");
      });
  }
</script>
{#each Object.entries(data) as [directory, items]}
<h3>Directory: {directory}</h3>
{#each items as item}
<pre title="{item.name}">{item.basename}</pre>
{#if item.importers.length} {#each item.importers as info}
<p class="flex-row">
  <AccountInput bind:value="{info.account}" />
  <input size="40" value="{info.newName}" />
  <button
    type="button"
    on:click="{() => move(item.name, info.account, info.newName)}"
  >
    {('Move')}
  </button>
  <a
    class="button"
    title="{_('Extract')} with importer {info.importer_name}"
    href="{extractURL(item.name, info.importer_name)}"
    >{('Extract')} ( {info.importer_name} )</a
  >
</p>
{/each} {:else}
<p>
  <AccountInput bind:value="{item.account}" />
  <input size="40" value="{item.newName}" />
  <button
    type="button"
    on:click="{() => move(item.name, item.account, item.newName)}"
  >
    {('Move')}
  </button>
</p>
{/if} {/each} {/each}
<style>
  .flex-row {
    display: flex;
  }
  .button {
    padding: 4px 8px;
  }

  .name {
    width: 16em;
    flex-shrink: 0;
    margin: 0 0.5em 0.5em 0;
  }

  table {
    width: 100%;
  }
</style>
