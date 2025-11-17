<script lang="ts">
  import type { EntryBaseAttributes } from "../entries/index.ts";
  import { urlForSource } from "../helpers.ts";
  import { _ } from "../i18n.ts";

  interface Props {
    entry: EntryBaseAttributes;
  }

  let { entry }: Props = $props();
</script>

<p>
  {_("Location")}:
  <code>
    <a href={$urlForSource(entry.meta.filename, entry.meta.lineno)}>
      {entry.meta.filename}:{entry.meta.lineno}
    </a>
  </code>
</p>

<style>
  code {
    display: inline-block;
    max-width: 80%;
    padding: 2px 4px;
    vertical-align: top;
  }
</style>
