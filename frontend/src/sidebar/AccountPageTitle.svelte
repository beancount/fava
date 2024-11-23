<script lang="ts">
  import { day } from "../format";
  import { urlForAccount } from "../helpers";
  import { account_details } from "../stores";
  import AccountIndicator from "./AccountIndicator.svelte";

  interface Props {
    account: string;
  }

  let { account }: Props = $props();

  let parts = $derived(account.split(":"));

  let details = $derived($account_details[account]);
  let last = $derived(details?.last_entry);
</script>

<span class="droptarget" data-account-name={account}>
  {#each parts as part, index}
    {@const name = parts.slice(0, index + 1).join(":")}<a
      href={$urlForAccount(name)}
      title={name}>{part}</a
    >{#if index < parts.length - 1}:{/if}{/each}
  <AccountIndicator {account} />
  {#if last}
    <span class="last-activity">
      (Last entry: <a href="#context-{last.entry_hash}">{day(last.date)}</a>)
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
