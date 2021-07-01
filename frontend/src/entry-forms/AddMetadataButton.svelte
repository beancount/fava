<script lang="ts">
  import type { EntryMetadata } from "../entries";
  import { _ } from "../i18n";

  export let meta: EntryMetadata;

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
