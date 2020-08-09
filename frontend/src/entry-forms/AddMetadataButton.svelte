<script>
  import { _ } from "../i18n";

  /** @type {Record<string, string>} */
  export let meta;

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
  title={_('Add metadata')}>
  m
</button>
