<script lang="ts">
  import type { EntryMetadata } from "../entries";
  import { _ } from "../i18n";

  interface Props {
    meta: EntryMetadata;
  }

  let { meta = $bindable() }: Props = $props();
</script>

<button
  type="button"
  class="muted round"
  onclick={() => {
    meta = meta.add();
  }}
  tabindex={-1}
  title={_("Add metadata")}
>
  m
</button>
