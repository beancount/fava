<script lang="ts">
  import JournalTable from "../../journal/JournalTable.svelte";
  import type { JournalProps } from ".";

  let { entries }: JournalProps = $props();
</script>

<JournalTable {entries} />
