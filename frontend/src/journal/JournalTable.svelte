<script lang="ts">
  import { createVirtualizer } from "@tanstack/svelte-virtual";
  import { onDestroy, type Snippet } from "svelte";
  import { derived } from "svelte/store";

  import type { Entry } from "../entries";
  import { _ } from "../i18n";
  import { DateColumn, type SortColumn, Sorter, StringColumn } from "../sort";
  import {
    journalShow as journalShowStore,
    type JournalShowEntry,
    type JournalSortOrder,
    journalSortOrder,
  } from "../stores/journal";
  import JournalEntry from "./JournalEntry.svelte";
  import JournalFilters from "./JournalFilters.svelte";
  import type { AccountJournalEntry } from "../api/validators";

  type E = Entry | AccountJournalEntry;
  interface Props {
    entries: E[];
    showChangeAndBalance?: boolean;
    header?: Snippet;
  }

  const { entries, showChangeAndBalance = false, header }: Props = $props();

  function entry(e: E | Readonly<E>): Entry {
    return Array.isArray(e) ? e[0] : (e as Entry);
  }

  let head = $state<HTMLLIElement>();
  $effect(() => {
    const order = $journalSortOrder;
    head?.querySelectorAll<HTMLSpanElement>("span[data-sort]").forEach((el) => {
      el.removeAttribute("data-order");
      if (el.getAttribute("data-sort-name") === order[0]) {
        el.setAttribute("data-order", order[1] ?? "asc");
      }
    });
  });

  let sortedEntries = $state.raw<E[]>([]);
  const journalShow = derived(journalShowStore, (t) => new Set(t));
  const filter = derived([journalSortOrder, journalShow], (it) => it);
  const unsub = filter.subscribe(([journalSortOrder, journalShow]) => {
    let column: SortColumn<E>;
    switch (journalSortOrder[0]) {
      case "flag":
        column = new StringColumn<E>("flag", (e) => entry(e).sortFlag);
        break;
      case "narration":
        column = new StringColumn("narration", (e) => entry(e).sortNarration);
        break;
      default:
        column = new DateColumn("date", (e) => entry(e).date);
        break;
    }
    const sorter = new Sorter(column, journalSortOrder[1] ?? "asc");

    const filtered = entries.filter((t) => {
      const e = entry(t);
      if (journalShow.has(e.t.toLowerCase() as JournalShowEntry)) {
        if (e.t === "Transaction") {
          let flagOpt: JournalShowEntry;
          switch (e.flag) {
            case "*":
              flagOpt = "cleared";
              break;
            case "!":
              flagOpt = "pending";
              break;
            default:
              flagOpt = "other";
          }
          return journalShow.has(flagOpt);
        } else if (e.t === "Document") {
          if (e.tags) {
            if (e.tags.includes("discovered")) {
              return journalShow.has("discovered");
            }
            if (e.tags.includes("linked")) {
              return journalShow.has("linked");
            }
          }
        } else if (e.t === "Custom") {
          if (e.type === "budget") {
            return journalShow.has("budget");
          }
        }
        return true;
      }
      return false;
    });

    sortedEntries = sorter.sort(filtered) as E[];
  });

  onDestroy(() => {
    unsub();
  });

  function headerClick(e: MouseEvent & { currentTarget: HTMLSpanElement }) {
    const name = e.currentTarget.getAttribute("data-sort-name");
    const order =
      e.currentTarget.getAttribute("data-order") === "asc" ? "desc" : "asc";
    $journalSortOrder = [name as JournalSortOrder[0], order];
  }

  let vlistOuter = $state<HTMLDivElement>();
  let vlistItems = $state<HTMLLIElement[]>([]);

  function depend<T, R>(t: T, fn: (t: T) => R) {
    return fn(t);
  }

  const getSortedEntry = $derived(
    depend(sortedEntries, (sortedEntries) => (i: number) => {
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      return sortedEntries[i]!;
    }),
  );

  let virtualizer = $derived(
    createVirtualizer({
      overscan: 5,
      count: sortedEntries.length + 1,
      getItemKey: depend(
        sortedEntries,
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        (sortedEntries) => (i) =>
          i === 0 ? "head" : entry(sortedEntries[i - 1]!).entry_hash,
      ),
      getScrollElement: depend(vlistOuter, (ol) => () => ol ?? null),
      estimateSize: () => 50,
    }),
  );

  let items = $derived($virtualizer.getVirtualItems());

  $effect(() => {
    if (head) $virtualizer.measureElement(head);
    if (vlistItems.length) {
      vlistItems.forEach((li) => {
        $virtualizer.measureElement(li);
      });
    }
  });
</script>

<div class="fixed-fullsize-container">
  <div bind:this={vlistOuter} class="vlist-outer">
    <div
      class="flex-table journal vlist-inner"
      style="height: {$virtualizer.getTotalSize()}px;"
    >
      <ol
        class="vlist-items"
        style="transform: translateY({items[0]?.start ?? 0}px);"
      >
        {#each items as row (row.index)}
          {#if row.index === 0}
            <li class="head" bind:this={head} data-index="0">
              {@render header?.()}
              <div class="filter-container">
                <JournalFilters />
              </div>
              <p>
                <!-- TODO: ARIA tags -->
                <span
                  class="datecell"
                  data-sort="date"
                  data-sort-name="date"
                  onclick={headerClick}
                  aria-hidden="true"
                >
                  {_("Date")}
                </span>
                <span
                  class="flag"
                  data-sort="string"
                  data-sort-name="flag"
                  onclick={headerClick}
                  aria-hidden="true"
                >
                  {_("F")}
                </span>
                <span
                  class="description"
                  data-sort="string"
                  data-sort-name="narration"
                  onclick={headerClick}
                  aria-hidden="true"
                >
                  {_("Payee")}/{_("Narration")}
                </span>
                <span class="num">{_("Units")}</span>
                <span class="cost num">
                  {_("Cost")}
                  {#if showChangeAndBalance}
                    / {_("Change")}
                  {/if}
                </span>
                <span class="num">
                  {_("Price")}
                  {#if showChangeAndBalance}
                    / {_("Balance")}
                  {/if}
                </span>
              </p>
            </li>
          {:else}
            <JournalEntry
              index={row.index}
              entry={getSortedEntry(row.index - 1)}
              {showChangeAndBalance}
              journalShow={$journalShow}
              bind:li={vlistItems[row.index]}
            />
          {/if}
        {/each}
      </ol>
    </div>
  </div>
</div>

<style>
  .fixed-fullsize-container {
    position: absolute;
    top: 0;
    left: 0;
  }

  .vlist-outer {
    height: 100%;
    padding: 1.5em;
    contain: strict;
    overflow-y: auto;
  }

  .vlist-inner {
    position: relative;
    width: 100%;
    margin: 0;
  }

  .vlist-items {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
  }

  .filter-container {
    margin-bottom: 0.25rem;
  }
</style>
