<script lang="ts">
  import AccountPageTitle from "./AccountPageTitle.svelte";
  import { page_title } from "./page-title";

  let { title, type } = $derived($page_title);

  let is_account = $derived(type === "account");
</script>

<strong>
  {#if !is_account}
    {title}
  {:else}
    <AccountPageTitle account={title} />
  {/if}
</strong>

<style>
  strong::before {
    margin: 0 10px;
    font-weight: normal;
    content: "›";
    opacity: 0.5;
  }
</style>
