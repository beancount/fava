<script lang="ts">
  import type { Entry } from "../entries/index.ts";
  import { url_for_source } from "../helpers.ts";
  import { _ } from "../i18n.ts";

  interface Props {
    entry: Entry;
  }

  let { entry }: Props = $props();
</script>

<p>
  {_("Location")}:
  <code>
    <a href={$url_for_source(entry.meta.filename, entry.meta.lineno)}>
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
