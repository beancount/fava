<script lang="ts">
  import { url_for } from "../helpers.ts";
  import { _ } from "../i18n.ts";
  import { hash } from "../stores/url.ts";
  import ModalBase from "./ModalBase.svelte";

  let shown = $derived($hash === "export");
</script>

<ModalBase {shown}>
  {#if shown}
    <div>
      <h3>{_("Export")}:</h3>
      <a href={$url_for("download-journal")} data-remote>
        {_("Download currently filtered entries as a Beancount file")}
      </a>
    </div>
  {/if}
</ModalBase>
