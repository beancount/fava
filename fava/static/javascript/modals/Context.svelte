<script>
  import { afterUpdate, onMount } from "svelte";

  import initSourceEditor from "../editor";
  import { fetch, delegate, handleText } from "../helpers";
  import { urlHash, favaAPI } from "../stores";

  import ModalBase from "./ModalBase.svelte";

  let div;
  $: shown = $urlHash.startsWith("context");
  $: entryHash = shown ? $urlHash.slice(8) : "";
  $: content = !shown
    ? ""
    : fetch(`${favaAPI.baseURL}_context/?entry_hash=${entryHash}`).then(
        handleText
      );

  onMount(() => {
    delegate(div, "click", ".toggle-box-header", event => {
      event.target.closest(".toggle-box").classList.toggle("toggled");
    });
  });

  afterUpdate(async () => {
    if (!content) {
      return;
    }
    await content;
    initSourceEditor("#source-slice-editor");
  });
</script>

<ModalBase {shown}>
  <div class="content" bind:this={div}>
    {#await content}
      Loading entry context...
    {:then html}
      {@html html}
    {:catch}
      Loading entry context failed.
    {/await}
  </div>
</ModalBase>
