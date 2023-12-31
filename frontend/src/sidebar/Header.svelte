<script lang="ts">
  import { keyboardShortcut } from "../keyboard-shortcuts";
  import router from "../router";
  import { ledger_title, ledgerData } from "../stores";

  import FilterForm from "./FilterForm.svelte";
  import HeaderIcon from "./HeaderIcon.svelte";
  import { has_changes } from "./page-title";
  import PageTitle from "./PageTitle.svelte";

  $: other_ledgers = $ledgerData.other_ledgers;
  $: has_dropdown = other_ledgers.length;
</script>

<header>
  <HeaderIcon />
  <h1>
    {$ledger_title}{#if has_dropdown}&nbsp;▾{/if}<PageTitle />
    <button
      type="button"
      hidden={!$has_changes}
      class="reload-page"
      use:keyboardShortcut={"r"}
      on:click={() => {
        router.reload();
      }}
    >
      &#8635;
    </button>
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
  <FilterForm />
</header>

<style>
  .reload-page {
    padding-right: 12px;
    padding-left: 12px;
    margin-top: -8px;
    margin-left: 20px;
    background-color: var(--warning);
  }

  h1 {
    display: block;
    flex: 1;
    max-height: var(--header-height);
    padding: calc((var(--header-height) - 24px) / 2) 10px;
    margin: 0;
    overflow: hidden;
    font-size: 16px;
    font-weight: normal;
    color: var(--header-color);
  }

  a:hover,
  a:link,
  a:visited {
    color: inherit;
  }

  .beancount-files {
    position: absolute;
    top: var(--header-height);
    left: 19px;
    z-index: var(--z-index-floating-ui);
    display: none;
    width: 20em;
    color: var(--link-color);
    background-color: var(--background);
    border: 1px solid var(--border);
    border-bottom-right-radius: 3px;
    border-bottom-left-radius: 3px;
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
