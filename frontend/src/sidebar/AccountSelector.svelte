<script lang="ts">
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import { urlForAccount } from "../helpers.ts";
  import { _ } from "../i18n.ts";
  import { router } from "../router.ts";
  import { accounts } from "../stores/index.ts";

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
    key="g a"
    onSelect={select}
    onEnter={select}
  />
</li>

<style>
  li {
    --input-border: none;
    --input-padding: 0.25em 0.5em 0.25em 1em;
    --autocomplete-list-position: fixed;
  }
</style>
