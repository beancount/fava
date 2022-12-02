<script lang="ts">
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import { _ } from "../i18n";
  import { date as validate_date } from "../lib/validation";
  import { account_details, accounts } from "../stores";

  export let value: string;
  export let suggestions: string[] | undefined = undefined;
  export let date: string | undefined = undefined;
  export let className: string | undefined = undefined;

  function checkValidity(val: string) {
    return !$accounts.length || $accounts.includes(val)
      ? ""
      : _("Should be one of the declared accounts");
  }

  function filterSuggestions(
    accounts_: string[],
    date_: string | undefined
  ): string[] {
    const res = validate_date(date_);
    if (!res.success) {
      return accounts_;
    }
    const entry_date = res.value;
    return accounts_.filter((account) => {
      const details = $account_details[account];
      if (!details) {
        return true;
      }
      return details.close_date >= entry_date;
    });
  }

  $: account_suggestions = suggestions ?? $accounts;
  $: filtered_suggestions = filterSuggestions(account_suggestions, date);
</script>

<AutocompleteInput
  placeholder={_("Account")}
  bind:value
  {className}
  {checkValidity}
  suggestions={filtered_suggestions}
/>
