<script lang="ts">
  import AutocompleteInput from "../components/AutocompleteInput.svelte";
  import { _ } from "../i18n.ts";
  import { account_details, currencies } from "../stores/index.ts";

  interface Props {
    /** The amount input value. */
    value: string;
    /** The account this amount is for - restricts currency suggestions if given. */
    account?: string | undefined;
  }

  let { value = $bindable(), account }: Props = $props();

  // Only the leading numeric part, so that digits in the currency
  // (e.g. typing "100 A123") are not picked up as part of the number.
  let number = $derived(
    /^-?[0-9]*\.?[0-9]*/.exec(value.trimStart())?.[0] ?? "",
  );
  // The currencies that the account is restricted to, falling back to all
  // currencies if the account has no restriction.
  let currency_options = $derived.by(() => {
    const account_currencies =
      account != null ? $account_details[account]?.currencies : null;
    return account_currencies != null && account_currencies.length > 0
      ? account_currencies
      : $currencies;
  });
  let suggestions = $derived(
    number ? currency_options.map((c) => `${number} ${c}`) : [],
  );
</script>

<AutocompleteInput
  bind:value
  placeholder={_("Amount")}
  {suggestions}
  automatic_selection={true}
/>
