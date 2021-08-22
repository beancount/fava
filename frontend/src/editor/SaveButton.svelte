<script lang="ts">
  import { _ } from "../i18n";
  import { modKey } from "../keyboard-shortcuts";

  export let changed: boolean;
  export let saving: boolean;

  $: buttonContent = saving ? _("Saving...") : _("Save");
</script>

<button disabled={!changed} title={`${_("Save")} (${modKey}+s)`}>
  {buttonContent}
</button>
