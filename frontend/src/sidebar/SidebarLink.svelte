<script lang="ts">
  import Link from "../components/Link.svelte";
  import type { KeySpec } from "../keyboard-shortcuts";

  export let report: string;
  export let name: string;
  export let key: KeySpec | undefined = undefined;
  export let remote: true | undefined = undefined;
  export let bubble: [number, "error" | "info"] | undefined = undefined;
</script>

<li class="sidebar-link">
  <Link {report} {key} {remote}>
    {name}
    {#if bubble && bubble[0] > 0}
      <span class="bubble" class:error={bubble[1] === "error"}>
        {bubble[0]}
      </span>
    {/if}
  </Link>
  <slot />
</li>

<style>
  .sidebar-link :global(a) {
    display: block;
    padding: 0.25em 0.5em 0.25em 1em;
    color: inherit;
  }

  .sidebar-link :global(a.selected),
  :global(a:hover) {
    color: var(--sidebar-hover-color);
    background-color: var(--sidebar-border);
  }

  li {
    display: flex;
    flex-wrap: wrap;
  }

  li:last-child {
    margin-bottom: 0;
    border: none;
  }

  .sidebar-link :global(a:first-child) {
    flex: 1;
  }

  .bubble {
    float: right;
    padding: 0 8px;
    font-size: 0.9em;
    color: var(--sidebar-color);
    background-color: var(--sidebar-border);
    border-radius: 12px;
  }

  .error.bubble {
    color: white;
    background-color: var(--error);
  }
</style>
