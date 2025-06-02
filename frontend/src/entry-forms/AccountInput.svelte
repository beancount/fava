<script lang="ts">
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import { _ } from "../i18n";
  import { date as validate_date } from "../lib/validation";
  import { accounts, accounts_set } from "../stores";
  import { is_closed_account } from "../stores/accounts";

  interface Props {
    /** The account name input value. */
    value: string;
    /** An optional list of accounts to suggest - otherwise the whole account list is used. */
    suggestions?: string[] | undefined;
    /** The date to enter this account for to exclude closed accounts. */
    date?: string | undefined;
    /** An optional class name to assign to the input element. */
    className?: string;
    /** Whether to mark the input as required. */
    required?: boolean;
  }

  let {
    value = $bindable(),
    suggestions,
    date,
    className,
    required,
  }: Props = $props();

  let checkValidity = $derived((val: string) =>
    !$accounts_set.size || $accounts_set.has(val) || (required !== true && !val)
      ? ""
      : _("Should be one of the declared accounts"),
  );

  let parsed_date = $derived(validate_date(date).unwrap_or(null));
  let account_suggestions = $derived(suggestions ?? $accounts);
  let filtered_suggestions = $derived(
    parsed_date
      ? account_suggestions.filter(
          (account) => !$is_closed_account(account, parsed_date),
        )
      : account_suggestions,
  );
</script>

<AutocompleteInput
  placeholder={_("Account")}
  bind:value
  {className}
  {checkValidity}
  {required}
  suggestions={filtered_suggestions}
/>
