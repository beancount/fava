<script>
  import { _ } from "../helpers";
  import { accounts } from "../stores";

  import AutocompleteInput from "../AutocompleteInput.svelte";

  export let value;
  export let suggestions = null;

  function checkValidity(val) {
    return $accounts.includes(val)
      ? ""
      : _("Should be one of the declared accounts");
  }
</script>

<AutocompleteInput
  className="account"
  placeholder={_('Account')}
  bind:value
  {checkValidity}
  suggestions={suggestions || $accounts} />
