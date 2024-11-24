<script lang="ts">
  interface Props {
    key: string[];
  }

  let { key }: Props = $props();
</script>

{#each key as part, index}
  <kbd>{part}</kbd>{index === key.length - 1 ? "" : "+"}
{/each}
