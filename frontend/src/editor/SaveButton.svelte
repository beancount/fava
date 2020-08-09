<script>
  import { _ } from "../i18n";

  /** @type {boolean} */
  export let changed;
  /** @type {boolean} */
  export let saving;

  $: buttonContent = saving ? _("Saving...") : _("Save");
</script>

<button disabled={!changed} title="{_('Save')} (Ctrl/Cmd+s)">
  {buttonContent}
</button>
