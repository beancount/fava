<script lang="ts">
  import { get } from "../api";
  import SliceEditor from "../editor/SliceEditor.svelte";
  import { urlHash } from "../stores";

  import ModalBase from "./ModalBase.svelte";

  $: shown = $urlHash.startsWith("context");
  $: entry_hash = shown ? $urlHash.slice(8) : "";
  $: content = shown ? get("context", { entry_hash }) : null;
</script>

<ModalBase {shown}>
  <div class="content">
    {#await content}
      Loading entry context...
    {:then response}
      {#if response}
        {@html response.content}
        <SliceEditor
          {entry_hash}
          slice={response.slice}
          sha256sum={response.sha256sum}
        />
      {/if}
    {:catch}
      Loading entry context failed...
    {/await}
  </div>
</ModalBase>
