<!--
  @component
  A sub-item in an app menu.
-->
<script lang="ts">
  import type { Snippet } from "svelte";

  interface Props {
    /** A title (optional) for the element. */
    title?: string;
    /** Whether this menu item should be marked as selected. */
    selected?: boolean;
    /** The action to execute on click. */
    action: () => void;
    children: Snippet;
    right?: Snippet;
  }

  let { title, selected = false, action, children, right }: Props = $props();
</script>

<li
  class:selected
  {title}
  role="menuitem"
  onclick={action}
  onkeydown={(event) => {
    if (event.key === "Enter") {
      action();
    }
  }}
>
  {@render children()}
  {#if right}
    <span>
      {@render right()}
    </span>
  {/if}
</li>

<style>
  .selected::before {
    content: "›";
  }

  li {
    padding: 0.25em 0.5em;
  }

  span {
    float: right;
  }

  li:hover,
  li:focus-visible {
    background-color: var(--background-darker);
  }
</style>
