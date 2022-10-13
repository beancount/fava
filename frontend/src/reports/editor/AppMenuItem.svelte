<!--
  @component
  A single top level menu item in an app menu.

  The default slot should filled with its vertically arranged sub-items.
-->
<script lang="ts">
  /** The name of the menu item. */
  export let name: string;

  let open = false;
</script>

<span
  class:open
  tabindex="0"
  role="menuitem"
  on:keydown={(ev) => {
    if (ev.key === "ArrowDown") {
      open = true;
    }
  }}
>
  {name}
  <ul role="menu">
    <slot />
  </ul>
</span>

<style>
  span {
    padding: 0.7rem 0.5rem;
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
    margin: 0.75rem 0 0 -0.5rem;
    overflow-y: auto;
    background-color: var(--background);
    border: 1px solid var(--border);
    border-bottom-right-radius: 3px;
    border-bottom-left-radius: 3px;
    box-shadow: 0 3px 6px var(--transparent-black);
  }

  span.open > ul,
  span:hover > ul {
    display: block;
  }
</style>
