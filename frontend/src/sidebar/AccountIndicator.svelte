<script lang="ts">
  import { ledgerData } from "../stores";

  export let account: string;

  $: account_details = $ledgerData.account_details[account];
  $: status = account_details?.uptodate_status;
  $: balance = account_details?.balance_string ?? "";
</script>

{#if status === "green"}
  <span
    class="status-indicator status-green"
    title="The last entry is a passing balance check."
  />
{:else if status}
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
