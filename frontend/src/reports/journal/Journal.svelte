<script lang="ts">
  import type { JournalReportProps } from "./index.ts";
  import JournalTable from "./JournalTable.svelte";

  let { journal, initial_sort, load_page, total_pages }: JournalReportProps =
    $props();
</script>

<JournalTable
  {journal}
  {initial_sort}
  {load_page}
  {total_pages}
  show_change_and_balance={false}
/>
