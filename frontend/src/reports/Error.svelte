<script lang="ts">
  import { errorWithCauses } from "../lib/errors";

  export let title: string;
  export let error: Error;
</script>

<h2>Loading {title} failed with error:</h2>

<pre>{errorWithCauses(error)}</pre>

<style>
  pre {
    color: var(--error);
  }
</style>
