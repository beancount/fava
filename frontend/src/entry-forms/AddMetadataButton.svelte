<script lang="ts">
  import { _ } from "../i18n";

  export let meta: Record<string, unknown>;

  function addMetadata() {
    meta[""] = "";
    meta = meta;
  }
</script>

<button
  class="muted round"
  type="button"
  on:click={addMetadata}
  tabindex={-1}
  title={_("Add metadata")}
>
  m
</button>
