<script>
  import { _ } from "../i18n";
  import { accounts } from "../stores";

  import AutocompleteInput from "../AutocompleteInput.svelte";

  /** @type {string} */
  export let value;
  /** @type {string[] | undefined} */
  export let suggestions = undefined;
  /** @type {string | undefined} */
  export let className = undefined;

  /**
   * @param {string} val
   */
  function checkValidity(val) {
    return !$accounts.length || $accounts.includes(val)
      ? ""
      : _("Should be one of the declared accounts");
  }
</script>

<AutocompleteInput
  placeholder={_("Account")}
  bind:value
  {className}
  {checkValidity}
  suggestions={suggestions || $accounts}
/>
