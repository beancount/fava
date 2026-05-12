<script lang="ts">
  import { untrack } from "svelte";

  import { _ } from "../../i18n.ts";
  import { get_el } from "../../lib/dom.ts";
  import { shallow_equal } from "../../lib/equals.ts";
  import { log_error } from "../../log.ts";
  import { is_supported_datatransfer } from "../../modals/document-upload.ts";
  import { is_loading, loading_state } from "../../router.ts";
  import {
    journal_show,
    journal_sort,
    type JournalSort,
  } from "../../stores/journal.ts";
  import { get_account_from_url } from "../accounts/index.ts";
  import { handle_journal_click } from "./click_handler.ts";
  import JournalFilters from "./JournalFilters.svelte";
  import JournalHeaders from "./JournalHeaders.svelte";
  import type { JournalSortColumn } from "./sort.ts";
  import { sort_journal } from "./sort.ts";

  interface Props {
    initial_sort: JournalSort;
    journal: DocumentFragment;
    load_page?: ((page: number) => Promise<DocumentFragment | null>) | null;
    show_change_and_balance: boolean;
    total_pages?: number;
  }

  let {
    initial_sort,
    journal,
    load_page,
    show_change_and_balance,
    total_pages = 1,
  }: Props = $props();

  let ol: HTMLOListElement | undefined = $state();

  /** Set the data attributes for drag-and-drop on dragenter */
  function ondragenter(event: DragEvent) {
    const closest_element = get_el(event.target);
    const description = closest_element?.closest(".description");
    // Get the closest `<li>` to also find the first posting account in a transaction.
    const li = description?.closest("li");
    if (
      description instanceof Element &&
      li &&
      is_supported_datatransfer(event.dataTransfer)
    ) {
      const account = [...li.querySelectorAll("a")]
        .map((a) => new URL(a.href))
        .map(get_account_from_url)
        .find((res) => res.is_ok)?.value;
      if (account != null) {
        description.setAttribute("data-account-name", account);
        description.classList.add("dragover");
        event.preventDefault();

        const date_link = description
          .closest(".journal > li")
          ?.querySelector(".datecell")
          ?.querySelector("a");
        if (date_link != null) {
          const entry_date = date_link.innerText;
          const hash = new URL(date_link.href).hash;
          if (hash.startsWith("#context-")) {
            const entry_hash = hash.slice(9);
            description.setAttribute("data-entry-date", entry_date);
            description.setAttribute("data-entry-hash", entry_hash);
          }
        }
      }
    }
  }
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
  {ondragenter}
  {@attach (node: HTMLOListElement) => {
    void journal;
    return untrack(() => {
      const sort = $journal_sort;
      node.innerHTML = "";
      node.append(journal);
      // If the data is already sorted by the fetched order, we do not need to sort again
      // For the non-datewise sorts, only sort once for the initial page and once at the end.
      const needs_sorting = !shallow_equal(sort, initial_sort);
      if (needs_sorting) {
        sort_journal(node, sort);
      }
      if (!load_page || total_pages <= 1) {
        return undefined;
      }

      const load_journal_page = load_page;
      const scroll_container = node.closest("article");
      let next_page = 2;
      let loading_next_page = false;

      function load_if_near_bottom() {
        const distance_to_bottom =
          scroll_container == null
            ? node.getBoundingClientRect().bottom - window.innerHeight
            : scroll_container.scrollHeight -
              scroll_container.scrollTop -
              scroll_container.clientHeight;

        if (distance_to_bottom < 1000) {
          load_next_page().catch(log_error);
        }
      }

      async function load_next_page() {
        if (loading_next_page || next_page > total_pages) {
          return;
        }
        loading_next_page = true;
        try {
          await loading_state.run(async () => {
            const fragment = await load_journal_page(next_page);
            next_page += 1;
            if (fragment) {
              node.append(fragment);
            }
            const current_sort = $journal_sort;
            if (!shallow_equal(current_sort, initial_sort)) {
              sort_journal(node, current_sort);
            }
          });
        } finally {
          loading_next_page = false;
        }
        requestAnimationFrame(load_if_near_bottom);
      }

      const scroll_target = scroll_container ?? window;
      scroll_target.addEventListener("scroll", load_if_near_bottom, {
        passive: true,
      });
      window.addEventListener("resize", load_if_near_bottom);
      requestAnimationFrame(load_if_near_bottom);

      return () => {
        scroll_target.removeEventListener("scroll", load_if_near_bottom);
        window.removeEventListener("resize", load_if_near_bottom);
      };
    });
  }}
></ol>
