<script lang="ts">
  import { _ } from "../i18n.ts";

  interface Props {
    ondelete: () => Promise<void>;
  }

  let { ondelete }: Props = $props();

  let deleting = $state(false);

  let content = $derived(deleting ? _("Deleting…") : _("Delete"));

  async function onclick() {
    deleting = true;
    try {
      await ondelete();
    } finally {
      deleting = false;
    }
  }
</script>

<button type="button" class="muted" {onclick} title={content}>
  {content}
</button>
