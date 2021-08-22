<script lang="ts">
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import { _ } from "../i18n";
  import { accounts } from "../stores";

  export let value: string;
  export let suggestions: string[] | undefined = undefined;
  export let className: string | undefined = undefined;

  function checkValidity(val: string) {
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
