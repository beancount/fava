<script>
  import { _ } from "../helpers";
  import { accounts } from "../stores";

  import AutocompleteInput from "../AutocompleteInput.svelte";

  export let value = "";
  export let suggestions = null;

  let input;

  function checkValidity(val) {
    if ($accounts.includes(val)) {
      input.setCustomValidity("");
    } else {
      input.setCustomValidity(_("Should be one of the declared accounts"));
    }
  }

  $: if (input) {
    checkValidity(value);
  }
</script>

<AutocompleteInput
  bind:this={input}
  className="account"
  placeholder={_('Account')}
  bind:value
  suggestions={suggestions || $accounts} />
