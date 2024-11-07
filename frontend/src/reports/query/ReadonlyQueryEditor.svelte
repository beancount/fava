<script lang="ts">
  import { initReadonlyQueryEditor } from "../../codemirror/setup";

  export let value: string;
  export let error = false;

  const { renderEditor } = initReadonlyQueryEditor(value);
</script>

<pre class:error use:renderEditor></pre>

<style>
  .error {
    border: 1px solid var(--error);
  }
</style>
