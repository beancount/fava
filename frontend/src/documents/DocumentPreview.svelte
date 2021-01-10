<script>
  import Editor from "../editor/Editor.svelte";
  import { fetch, handleText } from "../lib/fetch";
  import { ext } from "../lib/paths";

  import { baseURL } from "../stores/url";

  /** @type {string} */
  export let filename;

  $: extension = ext(filename);
  $: url = `${$baseURL}document/?filename=${filename}`;
</script>

{#if extension === "pdf"}
  <object title={filename} data={url} />
{:else if ["csv", "txt"].includes(extension)}
  {#await fetch(url).then(handleText)}
    Loading...
  {:then value}
    <Editor {value} />
  {/await}
{:else}
  Preview for file `{filename}` with file type `{extension}` is not implemented
{/if}

<style>
  object {
    width: 100%;
    height: 100%;
  }
</style>
