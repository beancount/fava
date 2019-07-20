<script>
  import { _ } from "../helpers";
  import { favaAPI } from "../stores";

  import AutocompleteInput from "../AutocompleteInput.svelte";

  export let value = "";

  let input;

  function checkValidity(val) {
    if (favaAPI.accounts.includes(val)) {
      input.setCustomValidity("");
    } else {
      input.setCustomValidity(_("Should be one of the declared accounts"));
    }
  }

  $: if (input) checkValidity(value);
</script>

<AutocompleteInput
  bind:this={input}
  class="account"
  name="payee"
  placeholder={_('Account')}
  bind:value
  suggestions={favaAPI.accounts} />
