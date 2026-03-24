<script lang="ts">
  import { _ } from "../i18n.ts";

  interface Props {
    deleting: boolean;
    onDelete: () => void;
  }

  let { deleting, onDelete }: Props = $props();

  let buttonContent = $derived(deleting ? _("Deleting…") : _("Delete"));
</script>

<button type="button" class="muted" onclick={onDelete} title={_("Delete")}>
  {buttonContent}
</button>
