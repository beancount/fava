<script lang="ts">
  import { _ } from "../i18n";
  import { keyboardShortcut } from "../keyboard-shortcuts";

  interface Props {
    /** Whether anything is changed - the button is disabled otherwise. */
    changed: boolean;
    /** Whether the contents are currently being saved. */
    saving: boolean;
  }

  let { changed, saving }: Props = $props();

  let buttonContent = $derived(saving ? _("Saving...") : _("Save"));
</script>

<button
  type="submit"
  disabled={!changed}
  use:keyboardShortcut={{ key: "Control+s", mac: "Meta+s" }}
>
  {buttonContent}
</button>
