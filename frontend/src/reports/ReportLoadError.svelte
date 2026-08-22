<script lang="ts">
  import { error_with_causes } from "../lib/errors.ts";

  interface Props {
    title: string;
    error: Error;
  }

  let { title, error }: Props = $props();
</script>

<h2>Loading {title} failed with error:</h2>

<pre>{error_with_causes(error)}</pre>

<style>
  pre {
    color: var(--error);
  }
</style>
