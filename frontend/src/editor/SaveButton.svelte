<script>
  import { _ } from "../i18n";
  import { modKey } from "../keyboard-shortcuts";

  /** @type {boolean} */
  export let changed;
  /** @type {boolean} */
  export let saving;

  $: buttonContent = saving ? _("Saving...") : _("Save");
</script>

<button disabled={!changed} title={`${_("Save")} (${modKey}+s)`}>
  {buttonContent}
</button>
