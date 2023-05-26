<script lang="ts">
  export let title: string;
  export let error: Error;
</script>

<h2>Loading {title} failed with error:</h2>

<p>{error.message}</p>

<style>
  p {
    color: var(--error);
  }
</style>
