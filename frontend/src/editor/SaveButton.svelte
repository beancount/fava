<script>
  import { _ } from "../helpers";

  export let changed;
  export let saving;

  $: buttonContent = saving ? _("Saving...") : _("Save");
</script>

<button disabled={!changed} title="{_('Save')} (Ctrl/Cmd+s)">
  {buttonContent}
</button>
