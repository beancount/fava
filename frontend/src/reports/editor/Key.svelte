<script lang="ts">
  export let key: string[];
</script>

{#each key as part, index}
  <kbd>{part}</kbd>{index === key.length - 1 ? "" : "+"}
{/each}
