<script lang="ts">
  import AsideContents from "./AsideContents.svelte";

  /** Whether the sidebar is currently shown. */
  let active = false;
  const toggle = () => {
    active = !active;
  };
</script>

{#if active}
  <div class="overlay" on:click={toggle} aria-hidden="true"></div>
{/if}
<div class:active class="aside-buttons">
  <button type="button" on:click={toggle}>☰</button>
  <a class="button" href="#add-transaction">+</a>
</div>
<aside class:active>
  <AsideContents />
</aside>

<style>
  aside {
    grid-area: aside;
    padding-top: 0.5rem;
    margin: 0;
    overflow-y: auto;
    color: var(--sidebar-color);
    background-color: var(--sidebar-background);
    border-right: 1px solid var(--sidebar-border);
  }

  .aside-buttons {
    display: none;
  }

  @media (width <= 767px) {
    :root {
      --aside-width: 200px;
    }

    aside {
      position: fixed;
      top: 0;
      bottom: 0;
      z-index: var(--z-index-floating-ui);
      width: var(--aside-width);
      margin-left: calc(-1 * var(--aside-width));
      transition: var(--transitions);
    }

    .overlay {
      position: fixed;
      inset: 0;
      z-index: var(--z-index-floating-ui);
      cursor: pointer;
      background: var(--overlay-wrapper-background);
      transition: var(--transitions);
    }

    aside.active {
      margin-left: 0;
    }

    .aside-buttons {
      position: fixed;
      top: 0;
      left: 0;
      z-index: var(--z-index-floating-ui);
      display: flex;
      flex-direction: column;
      transition: var(--transitions);
    }

    .active.aside-buttons {
      left: var(--aside-width);
    }

    .aside-buttons > * {
      width: 42px;
      height: 42px;
      color: var(--mobile-button-text);
      text-align: center;
      background-color: var(--sidebar-background);
      border: 1px solid var(--sidebar-border);
    }

    .aside-buttons a {
      font-size: 28px;
    }
  }

  @media print {
    aside,
    .aside-buttons {
      display: none;
    }
  }
</style>
