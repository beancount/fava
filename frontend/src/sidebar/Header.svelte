<script lang="ts">
  import { keyboardShortcut } from "../keyboard-shortcuts";
  import router from "../router";
  import { ledger_title, ledgerData } from "../stores";
  import FilterForm from "./FilterForm.svelte";
  import HeaderIcon from "./HeaderIcon.svelte";
  import { has_changes } from "./page-title";
  import PageTitle from "./PageTitle.svelte";

  let other_ledgers = $derived($ledgerData.other_ledgers);
  let has_dropdown = $derived(other_ledgers.length);
</script>

<header>
  <HeaderIcon />
  <h1>
    {$ledger_title}{#if has_dropdown}&nbsp;▾{/if}<PageTitle />
    {#if has_dropdown}
      <div class="beancount-files">
        <ul>
          {#each other_ledgers as [name, url]}
            <li>
              <a href={url} data-remote>{name}</a>
            </li>
          {/each}
        </ul>
      </div>
    {/if}
  </h1>
  <button
    type="button"
    hidden={!$has_changes}
    class="reload-page"
    use:keyboardShortcut={"r"}
    onclick={router.reload.bind(router)}
  >
    &#8635;
  </button>
  <span class="spacer"></span>
  <FilterForm />
</header>

<style>
  .reload-page {
    background-color: var(--warning);
  }

  h1 {
    display: inline-block;
    padding: 0.5rem;
    margin: 0;
    overflow: hidden;
    font-size: 16px;
    font-weight: normal;
  }

  a:hover,
  a:link,
  a:visited {
    color: inherit;
  }

  .beancount-files {
    position: absolute;
    z-index: var(--z-index-floating-ui);
    display: none;
    width: 20em;
    margin-top: 0.25em;
    color: var(--link-color);
    background-color: var(--background);
    border: 1px solid var(--border);
    box-shadow: var(--box-shadow-dropdown);
  }

  .beancount-files a {
    display: block;
    padding: 8px 12px 8px 28px;
    cursor: pointer;
  }

  h1:hover .beancount-files {
    display: block;
  }

  .beancount-files ul {
    max-height: 400px;
    margin-bottom: 0;
    overflow-y: auto;
  }

  .beancount-files a:hover {
    color: var(--background);
    background-color: var(--link-color);
  }
</style>
