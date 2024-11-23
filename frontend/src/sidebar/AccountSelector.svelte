<script lang="ts">
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import { urlForAccount } from "../helpers";
  import { _ } from "../i18n";
  import router from "../router";
  import { accounts } from "../stores";

  let value = $state("");

  function select(el: HTMLInputElement) {
    if (value) {
      router.navigate($urlForAccount(value));
      el.blur();
      value = "";
    }
  }
</script>

<li>
  <AutocompleteInput
    bind:value
    placeholder={_("Go to account")}
    suggestions={$accounts}
    className="account-selector"
    key="g a"
    onSelect={select}
    onEnter={select}
  />
</li>

<style>
  :global(.account-selector input) {
    padding: 0.25em 0.5em 0.25em 1em;
    border: none;
  }
</style>
