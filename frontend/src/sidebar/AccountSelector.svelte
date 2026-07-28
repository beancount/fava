<script lang="ts">
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import { urlForAccount } from "../helpers.ts";
  import { _ } from "../i18n.ts";
  import { router } from "../router.ts";
  import { accounts } from "../stores/index.ts";

  let value = $state("");
  let autocomplete = $state.raw<{ blur: () => void }>();

  function select() {
    if (value) {
      router.navigate($urlForAccount(value));
      autocomplete?.blur();
      value = "";
    }
  }
</script>

<li>
  <AutocompleteInput
    bind:value
    bind:this={autocomplete}
    placeholder={_("Go to account")}
    suggestions={$accounts}
    key="g a"
    onselect={select}
    onenter={select}
  />
</li>

<style>
  li {
    --input-border: none;
    --input-padding: 0.25em 0.5em 0.25em 1em;
    --autocomplete-list-position: fixed;
  }
</style>
