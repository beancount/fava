<script lang="ts">
  import { initReadonlyQueryEditor } from "../../codemirror/setup";

  export let value: string;
  export let error = false;

  const [, useEditor] = initReadonlyQueryEditor(value);
</script>

<pre class:error use:useEditor />

<style>
  .error {
    border: 1px solid var(--error);
  }
</style>
