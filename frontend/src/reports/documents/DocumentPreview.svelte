<!--
  @component
  A component to show PDFs, text, images, and HTML files.
-->
<script lang="ts" context="module">
  /** For these file extensions we show a plain-text read-only editor. */
  const plainTextExtensions = ["csv", "json", "qfx", "txt", "xml"];
  /** For these file extensions we try to show the file as an `<img>` */
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
  import DocumentPreviewEditor from "../../editor/DocumentPreviewEditor.svelte";
  import { ext } from "../../lib/paths";
  import { base_url } from "../../stores";

  export let filename: string;

  $: extension = ext(filename).toLowerCase();
  $: url = `${$base_url}document/?filename=${encodeURIComponent(filename)}`;
</script>

{#if extension === "pdf"}
  <object title={filename} data={url} />
{:else if plainTextExtensions.includes(extension)}
  <DocumentPreviewEditor {url} />
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
