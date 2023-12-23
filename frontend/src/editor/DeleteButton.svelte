<script lang="ts">
  import { _ } from "../i18n";

  export let deleting: boolean;
  export let onDelete: () => void;

  $: buttonContent = deleting ? _("Deleting...") : _("Delete");
</script>

<button type="button" class="muted" on:click={onDelete} title={_("Delete")}>
  {buttonContent}
</button>
