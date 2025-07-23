<script lang="ts">
  import type { JournalProps } from ".";
  import JournalTable from "../../journal/JournalTable.svelte";

  let { entries }: JournalProps = $props();
</script>

<JournalTable {entries}/>
