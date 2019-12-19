<script>
  import { _ } from "../helpers";
  import { favaAPI } from "../stores";

  import AutocompleteInput from "../AutocompleteInput.svelte";

  export let value = "";
  export let suggestions;

  let input;

  function checkValidity(val) {
    if (favaAPI.accounts.includes(val)) {
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
  suggestions={suggestions || favaAPI.accounts} />
