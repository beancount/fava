<!--
  @component
  A sub-item in an app menu.
-->
<script lang="ts">
  /** A title (optional) for the element. */
  export let title: string | undefined = undefined;
  /** Whether this menu item should be marked as selected. */
  export let selected = false;
  /** The action to execute on click. */
  export let action: () => void;
</script>

<li class:selected {title}>
  <button type="button" on:click={action}>
    <slot />
    {#if $$slots.right}
      <span>
        <slot name="right" />
      </span>
    {/if}
  </button>
</li>

<style>
  .selected::before {
    content: "›";
  }

  li {
    padding: 0.25em 0.5em;
    cursor: pointer;
  }

  span {
    float: right;
  }

  button {
    display: contents;
    color: inherit;
  }

  li:hover,
  li:focus-visible {
    background-color: var(--background-darker);
  }
</style>
