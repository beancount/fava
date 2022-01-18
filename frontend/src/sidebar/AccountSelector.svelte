<script lang="ts">
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import { urlForAccount } from "../helpers";
  import { _ } from "../i18n";
  import router from "../router";
  import { accounts } from "../stores";

  let value = "";

  function select(ev: CustomEvent<HTMLInputElement>) {
    if (value) {
      router.navigate(urlForAccount(value));
      ev.detail.blur();
      value = "";
    }
  }
</script>

<AutocompleteInput
  bind:value
  placeholder={_("Go to account")}
  suggestions={$accounts}
  className="account-selector"
  key="g a"
  on:select={select}
  on:enter={select}
/>

<style>
  :global(.account-selector input) {
    padding: 0.25em 0.5em 0.25em 1em;
    border: none;
  }
</style>
