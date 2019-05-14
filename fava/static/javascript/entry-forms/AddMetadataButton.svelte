<script>
  import { _ } from "../helpers";

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
  title={_('Add metadata')}>
  m
</button>
