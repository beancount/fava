<script lang="ts">
  import type { Entry } from "../entries/index.ts";
  import { _ } from "../i18n.ts";

  interface Props {
    entry: Entry;
  }

  let { entry }: Props = $props();
</script>

<p>
  {_("Location")}:
  <code>
    {entry.meta.filename}:{entry.meta.lineno}
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
