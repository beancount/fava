<script lang="ts">
  import { urlFor } from "../helpers";
  import { _ } from "../i18n";
  import { urlHash } from "../stores/url";
  import ModalBase from "./ModalBase.svelte";

  $: shown = $urlHash === "export";
</script>

<ModalBase {shown}>
  {#if shown}
    <div>
      <h3>{_("Export")}:</h3>
      <a href={$urlFor("download-journal")} data-remote>
        {_("Download currently filtered entries as a Beancount file")}
      </a>
    </div>
  {/if}
</ModalBase>
