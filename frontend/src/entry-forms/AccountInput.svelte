<script lang="ts">
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import { _ } from "../i18n";
  import { date as validate_date } from "../lib/validation";
  import { accounts } from "../stores";
  import { is_closed_account } from "../stores/accounts";

  /** The account name input value. */
  export let value: string;
  /** An optional list of accounts to suggest - otherwise the whole account list is used. */
  export let suggestions: string[] | undefined = undefined;
  /** The date to enter this account for to exclude closed accounts. */
  export let date: string | undefined = undefined;
  /** An optional class name to assign to the input element. */
  export let className: string | undefined = undefined;

  $: checkValidity = (val: string) =>
    !$accounts.length || $accounts.includes(val) || !val
      ? ""
      : _("Should be one of the declared accounts");

  $: parsed_date = validate_date(date).unwrap_or(null);
  $: account_suggestions = suggestions ?? $accounts;
  $: filtered_suggestions = parsed_date
    ? account_suggestions.filter(
        (account) => !$is_closed_account(account, parsed_date),
      )
    : account_suggestions;
</script>

<AutocompleteInput
  placeholder={_("Account")}
  bind:value
  {className}
  {checkValidity}
  suggestions={filtered_suggestions}
/>
