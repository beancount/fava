<script lang="ts">
  import { attach_editor } from "../../codemirror/dom.ts";
  import type { CodemirrorBql } from "../../codemirror/types.ts";

  interface Props {
    value: string;
    error?: boolean | undefined;
    codemirror_bql: CodemirrorBql;
  }

  let { value, error = false, codemirror_bql }: Props = $props();

  let editor = $derived(codemirror_bql.init_readonly_query_editor(value));
</script>

<pre class:error {@attach attach_editor(editor)}></pre>

<style>
  .error {
    border: 1px solid var(--error);
  }
</style>
