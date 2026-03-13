<script lang="ts">
  import { _ } from "../i18n.ts";

  interface Props {
    onDuplicate: () => void;
  }

  let { onDuplicate }: Props = $props();

  let buttonContent = _("Duplicate");
</script>

<button
  type="button"
  class="muted"
  onclick={onDuplicate}
  title={_("Duplicate")}
>
  {buttonContent}
</button>
