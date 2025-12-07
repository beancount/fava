<script lang="ts">
  import { initReadonlyQueryEditor } from "../../codemirror/setup.ts";

  interface Props {
    value: string;
    error?: boolean | undefined;
  }

  let { value, error = false }: Props = $props();

  // This component is not used with updating values
  // svelte-ignore state_referenced_locally
  const { renderEditor } = initReadonlyQueryEditor(value);
</script>

<pre class:error {@attach renderEditor}></pre>

<style>
  .error {
    border: 1px solid var(--error);
  }
</style>
