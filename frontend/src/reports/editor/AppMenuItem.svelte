<!--
  @component
  A single top level menu item in an app menu.

  The default slot should filled with its vertically arranged sub-items.
-->
<script lang="ts">
  import type { Snippet } from "svelte";

  interface Props {
    /** The name of the menu item. */
    name: string;
    children: Snippet;
  }

  let { name, children }: Props = $props();

  let open = $state(false);
</script>

<span
  class:open
  tabindex="0"
  role="menuitem"
  onblur={() => {
    open = false;
  }}
  onkeydown={(event) => {
    if (event.key === "Escape") {
      open = false;
    } else if (event.key === "ArrowDown") {
      open = true;
    }
  }}
>
  {name}
  <ul role="menu">
    {@render children()}
  </ul>
</span>

<style>
  span {
    padding: 0.7em 0.5em;
    cursor: pointer;
  }

  span.open,
  span:hover {
    background-color: var(--background-darker);
  }

  span::after {
    content: "▾";
  }

  ul {
    position: absolute;
    z-index: var(--z-index-floating-ui);
    display: none;
    width: 500px;
    max-height: 400px;
    margin: 0.7em 0 0 -0.5em; /* The top margin should match the (bottom) padding of the span above. */
    overflow-y: auto;
    background-color: var(--background);
    border: 1px solid var(--border);
    box-shadow: var(--box-shadow-dropdown);
  }

  span.open > ul,
  span:hover > ul {
    display: block;
  }
</style>
