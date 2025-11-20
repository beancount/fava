<script lang="ts">
  import type { JournalReportProps } from "./index.ts";
  import JournalTable from "./JournalTable.svelte";

  let { journal, initial_sort, all_pages }: JournalReportProps = $props();
</script>

<JournalTable
  {journal}
  {initial_sort}
  {all_pages}
  show_change_and_balance={false}
/>
