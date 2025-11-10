<script lang="ts">
  import { untrack } from "svelte";

  import { _ } from "../../i18n.ts";
  import { shallow_equal } from "../../lib/equals.ts";
  import { log_error } from "../../log.ts";
  import { is_loading, loading_state } from "../../router.ts";
  import {
    journal_show,
    journal_sort,
    type JournalSort,
  } from "../../stores/journal.ts";
  import { handle_journal_click } from "./click_handler.ts";
  import JournalFilters from "./JournalFilters.svelte";
  import JournalHeaders from "./JournalHeaders.svelte";
  import type { JournalSortColumn } from "./sort.ts";
  import { sort_journal } from "./sort.ts";

  interface Props {
    all_pages?: Promise<DocumentFragment | null>[];
    initial_sort: JournalSort;
    journal: DocumentFragment;
    show_change_and_balance: boolean;
  }

  let {
    all_pages = [],
    initial_sort,
    journal,
    show_change_and_balance,
  }: Props = $props();

  let ol: HTMLOListElement | undefined = $state();
</script>

<JournalFilters />
<JournalHeaders
  disabled={$is_loading}
  {show_change_and_balance}
  set_sort_column={(column: JournalSortColumn) => {
    const sort: JournalSort = [
      column,
      shallow_equal($journal_sort, [column, "asc"]) ? "desc" : "asc",
    ];
    if (ol) {
      sort_journal(ol, sort);
      $journal_sort = sort;
    }
  }}
/>
<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<ol
  class={["flex-table", "journal", ...$journal_show.map((s) => `show-${s}`)]}
  bind:this={ol}
  onclick={handle_journal_click}
  {@attach (node: HTMLOListElement) => {
    void journal;
    untrack(() => {
      const sort = $journal_sort;
      node.innerHTML = "";
      node.append(journal);
      // If the data is already sorted by the fetched order, we do not need to sort again
      // For the non-datewise sorts, only sort once for the initial page and once at the end.
      const needs_sorting = !shallow_equal(sort, initial_sort);
      if (needs_sorting) {
        sort_journal(node, sort);
      }
      if (all_pages.length > 0) {
        loading_state
          .run(async () => {
            for (const page of all_pages) {
              const fragment = await page;
              if (fragment) {
                node.append(fragment);
              }
            }
            if (needs_sorting) {
              sort_journal(node, sort);
            }
          })
          .catch(log_error);
      }
    });
  }}
></ol>
