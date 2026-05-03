<script lang="ts">
  import type { EntryBaseAttributes } from "../entries/index.ts";
  import { _ } from "../i18n.ts";
  import SourceLink from "../SourceLink.svelte";

  interface Props {
    entry: EntryBaseAttributes;
  }

  let { entry }: Props = $props();
  let line = $derived(entry.meta.lineno);
</script>

<p>
  {_("Location")}:
  <code>
    <SourceLink
      file_path={entry.meta.filename}
      {line}
      label={`${entry.meta.filename}:${entry.meta.lineno}`}
    />
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
