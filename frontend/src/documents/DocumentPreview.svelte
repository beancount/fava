<script lang="ts" context="module">
  const plainTextExtensions = ["csv", "txt", "qfx"];
  const imageExtensions = [
    "gif",
    "jpg",
    "jpeg",
    "png",
    "svg",
    "webp",
    "bmp",
    "ico",
  ];
</script>

<script lang="ts">
  import Editor from "../editor/Editor.svelte";
  import { fetch, handleText } from "../lib/fetch";
  import { ext } from "../lib/paths";
  import { baseURL } from "../stores";

  export let filename: string;

  $: extension = ext(filename).toLowerCase();
  $: url = `${$baseURL}document/?filename=${filename}`;
</script>

{#if extension === "pdf"}
  <object title={filename} data={url} />
{:else if plainTextExtensions.includes(extension)}
  {#await fetch(url).then(handleText)}
    Loading...
  {:then value}
    <Editor {value} />
  {/await}
{:else if imageExtensions.includes(extension)}
  <img src={url} alt={filename} />
{:else if ["html", "htm"].includes(extension)}
  <iframe src={url} title={filename} sandbox="" />
{:else}
  Preview for file `{filename}` with file type `{extension}` is not implemented
{/if}

<style>
  object,
  img,
  iframe {
    width: 100%;
    height: 100%;
  }
  img {
    object-fit: contain;
  }
</style>
