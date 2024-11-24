<!--
  @component
  An application menu.
-->
<script lang="ts">
  import type { Snippet } from "svelte";

  interface Props {
    children: Snippet;
  }

  let { children }: Props = $props();
</script>

<div role="menubar">
  {@render children()}
</div>

<style>
  div {
    display: flex;
    gap: 0.5em;
    align-items: stretch;
    margin-right: 0.5em;
  }
</style>
