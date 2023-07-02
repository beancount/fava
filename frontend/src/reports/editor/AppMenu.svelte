<!--
  @component
  An application menu.
-->

<div role="menubar">
  <slot />
</div>

<style>
  div {
    display: flex;
    gap: 0.5em;
    align-items: stretch;
    margin-right: 0.5em;
  }
</style>
