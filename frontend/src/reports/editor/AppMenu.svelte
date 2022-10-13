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
    gap: 0.5rem;
    align-items: stretch;
    height: 100%;
    margin-right: 0.5rem;
  }
</style>
