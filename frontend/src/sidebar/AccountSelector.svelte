<script>
  import { _ } from "../i18n";
  import { accounts } from "../stores";
  import router from "../router";
  import { urlFor } from "../helpers";
  import AutocompleteInput from "../AutocompleteInput.svelte";

  let value = "";

  /**
   * @param {CustomEvent<HTMLInputElement>} ev
   */
  function select(ev) {
    if (value) {
      router.navigate(urlFor(`account/${value}`));
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
