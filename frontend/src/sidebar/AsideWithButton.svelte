<script lang="ts">
  import Aside from "./Aside.svelte";

  let active = false;
  const toggle = () => {
    active = !active;
  };
</script>

<button type="button" class:active on:click={toggle}>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    height="32px"
    width="32px"
    version="1.0"
    viewBox="0 0 24 24"
  >
    <circle cx="12" cy="5" r="2" />
    <circle cx="12" cy="12" r="2" />
    <circle cx="12" cy="19" r="2" />
  </svg>
</button>
<a href="#add-transaction" class:active class="add-transaction">+</a>
<aside class:active>
  <Aside />
</aside>

<style>
  aside {
    position: fixed;
    top: var(--header-height);
    bottom: 0;
    left: 0;
    z-index: var(--z-index-aside);
    width: var(--aside-width);
    padding-top: 0.5rem;
    margin: 0;
    overflow-y: auto;
    color: var(--sidebar-color);
    background-color: var(--sidebar-background);
    border-right: 1px solid var(--sidebar-border);
  }

  .add-transaction,
  button {
    z-index: var(--z-index-floating-ui);
    display: none;
    background-color: var(--sidebar-background);
  }

  .add-transaction,
  button:hover {
    background-color: var(--sidebar-background);
  }

  @media (width <= 767px) {
    aside {
      top: 0;
      margin-left: calc(-1 * var(--aside-width));
      transition: var(--transitions);
    }

    aside.active {
      margin-left: 0;
    }

    .add-transaction,
    button {
      position: fixed;
      left: 0;
      display: block;
      width: 42px;
      height: 42px;
      margin-left: 0;
      color: var(--mobile-button-text);
      text-align: center;
      border-color: var(--sidebar-border);
      border-style: solid;
      border-width: 1px;
      transition: var(--transitions);
    }

    button {
      top: 0;
      padding: 4px;
    }

    .add-transaction {
      top: 42px;
      font-size: 28px;
    }

    .active.add-transaction,
    button.active {
      left: var(--aside-width);
      background-color: var(--sidebar-background);
      box-shadow: unset;
    }
  }

  @media print {
    aside,
    a,
    button {
      display: none;
    }
  }
</style>
