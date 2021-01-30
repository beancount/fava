<script>
  /** @type {string} */
  export let key;
  $: parts = key.split("+");
</script>

{#each parts as part, index}
  <kbd>{part}</kbd>{index === parts.length - 1 ? "" : "+"}
{/each}
