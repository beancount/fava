<script lang="ts">
  import { urlForAccount } from "../helpers";
  import { ledgerData } from "../stores";

  import AccountIndicator from "./AccountIndicator.svelte";

  export let account: string;

  $: parts = account.split(":");

  $: account_details = $ledgerData.account_details[account];
  $: last = account_details?.last_entry;
</script>

<span class="droptarget" data-account-name={account}>
  {#each parts as part, index}
    {@const name = parts.slice(0, index + 1).join(":")}<a
      href={urlForAccount(name)}
      title={name}>{part}</a
    >{#if index < parts.length - 1}:{/if}{/each}
  <AccountIndicator {account} />
  <!-- TODO 
    {%- if account_name and ledger.accounts[account_name].meta.get('fava-uptodate-indication') -%}
    {{ last_account_activity(ledger, account_name) }}
    {%- endif -%}
    -->
  {#if last}
    <span class="last-activity">
      (Last entry: <a href="#context-{last.entry_hash}">{last.date}</a>)
    </span>
  {/if}
</span>

<style>
  a {
    color: unset;
  }

  .droptarget {
    padding: 0.6em;
    margin-left: -0.6em;
  }

  .last-activity {
    display: inline-block;
    margin-left: 10px;
    font-size: 12px;
    font-weight: normal;
    opacity: 0.8;
  }
</style>
