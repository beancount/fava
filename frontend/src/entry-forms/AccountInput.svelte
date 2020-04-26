<script>
  import { _ } from "../helpers";
  import { accounts } from "../stores";

  import AutocompleteInput from "../AutocompleteInput.svelte";

  export let value;
  export let suggestions = null;
  export let className = null;

  function checkValidity(val) {
    return !$accounts.length || $accounts.includes(val)
      ? ""
      : _("Should be one of the declared accounts");
  }
</script>

<AutocompleteInput
  placeholder={_('Account')}
  bind:value
  {className}
  {checkValidity}
  suggestions={suggestions || $accounts} />
