<script lang="ts">
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import { urlFor } from "../helpers";
  import { _ } from "../i18n";
  import router from "../router";
  import { accounts } from "../stores";

  let value = "";

  function select(ev: CustomEvent<HTMLInputElement>) {
    if (value) {
      router.navigate(urlFor(`account/${value}/`));
      ev.detail.blur();
      value = "";
    }
  }
</script>

<AutocompleteInput
  bind:value
  placeholder={_("Go to account")}
  selectFirst={true}
  suggestions={$accounts}
  key="g a"
  on:select={select}
/>
