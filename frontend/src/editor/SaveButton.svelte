<script lang="ts">
  import { _ } from "../i18n";
  import { keyboardShortcut } from "../keyboard-shortcuts";

  export let changed: boolean;
  export let saving: boolean;

  $: buttonContent = saving ? _("Saving...") : _("Save");
</script>

<button
  type="submit"
  disabled={!changed}
  use:keyboardShortcut={{ key: "Control+s", mac: "Meta+s" }}
>
  {buttonContent}
</button>
