<script lang="ts">
  import { initReadonlyQueryEditor } from "../../codemirror/setup";

  interface Props {
    value: string;
    error?: boolean | undefined;
  }

  let { value, error = false }: Props = $props();

  const { renderEditor } = initReadonlyQueryEditor(value);
</script>

<pre class:error use:renderEditor></pre>

<style>
  .error {
    border: 1px solid var(--error);
  }
</style>
