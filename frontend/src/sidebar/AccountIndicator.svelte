<script lang="ts">
  import { timeDay } from "d3-time";

  import { account_details, fava_options } from "../stores";

  /** The account name. */
  export let account: string;

  $: details = $account_details[account];
  $: status = details?.uptodate_status;
  $: balance = details?.balance_string ?? "";
  $: last_entry = details?.last_entry;

  $: last_account_activity = last_entry
    ? timeDay.count(last_entry.date, new Date())
    : 0;
</script>

{#if status}
  {#if status === "green"}
    <span
      class="status-indicator status-green"
      title="The last entry is a passing balance check."
    />
  {:else}
    <copyable-text
      class="status-indicator status-{status}"
      title={`${
        status === "yellow"
          ? "The last entry is not a balance check."
          : "The last entry is a failing balance check."
      }

Click to copy the balance directives to the clipboard:

${balance}`}
      data-clipboard-text={balance}
    />
  {/if}
  {#if last_account_activity > $fava_options.uptodate_indicator_grey_lookback_days}
    <span
      class="status-indicator status-gray"
      title="This account has not been updated in a while. ({last_account_activity} days ago)"
    />
  {/if}
{/if}

<style>
  .status-indicator {
    width: 10px;
    height: 10px;
    margin: 0 0 0 10px;
    border-radius: 10px;
  }

  .status-indicator.status-gray {
    margin-left: 0;
  }
</style>
