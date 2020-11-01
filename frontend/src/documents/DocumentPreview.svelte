<script>
  import { ext } from "../lib/paths";

  import { baseURL } from "../stores/url";

  /** @type {string} */
  export let filename;

  $: extension = ext(filename);
  $: url = `${$baseURL}document/?filename=${filename}`;
</script>

<style>
  object {
    width: 100%;
    height: 100%;
  }
</style>

{#if extension === 'pdf'}
  <object title={filename} data={url} />
{:else}
  Preview for file `{filename}` with file type `{extension}` is not implemented
{/if}
