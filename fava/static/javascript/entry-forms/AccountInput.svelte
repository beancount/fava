<script>
  import { _ } from "../helpers";
  import { favaAPI } from "../stores";

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

<input
  type="text"
  class="account"
  placeholder={_('Account')}
  list="accounts"
  bind:this={input}
  bind:value />
