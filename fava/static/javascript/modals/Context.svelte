<script>
  import { afterUpdate } from "svelte";

  import initSourceEditor from "../editor";
  import { fetch, handleText } from "../helpers";
  import { urlHash, favaAPI } from "../stores";

  import ModalBase from "./ModalBase.svelte";

  $: shown = $urlHash.startsWith("context");
  $: entryHash = shown ? $urlHash.slice(8) : "";
  $: content = !shown
    ? ""
    : fetch(`${favaAPI.baseURL}_context/?entry_hash=${entryHash}`).then(
        handleText
      );

  afterUpdate(async () => {
    if (!content) {
      return;
    }
    await content;
    initSourceEditor("#source-slice-editor");
  });
</script>

<ModalBase {shown}>
  <div class="content">
    {#await content}
      Loading entry context...
    {:then html}
      {@html html}
    {:catch}
      Loading entry context failed.
    {/await}
  </div>
</ModalBase>
