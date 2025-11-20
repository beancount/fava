<script lang="ts">
  import type { EntryMetadata } from "../entries/index.ts";
  import { _ } from "../i18n.ts";

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
