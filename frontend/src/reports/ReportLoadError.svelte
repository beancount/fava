<script lang="ts">
  import { errorWithCauses } from "../lib/errors";

  interface Props {
    title: string;
    error: Error;
  }

  let { title, error }: Props = $props();
</script>

<h2>Loading {title} failed with error:</h2>

<pre>{errorWithCauses(error)}</pre>

<style>
  pre {
    color: var(--error);
  }
</style>
