<script lang="ts">
  import type { Entry } from "../entries";
  import { _ } from "../i18n";
  import JournalEntry from "./JournalEntry.svelte";
  import {
    journalShow as journalShowStore,
    journalSortOrder,
    type JournalShowEntry,
    type JournalSortOrder,
  } from "../stores/journal";
  import { DateColumn, Sorter, StringColumn, type SortColumn } from "../sort";
  import JournalFilters from "./JournalFilters.svelte";
  import { onDestroy, onMount } from "svelte";
  import { derived } from "svelte/store";
  import { createVirtualizer } from "@tanstack/svelte-virtual";

  interface Props {
    entries: Entry[];
    showChangeAndBalance?: boolean;
  }

  const { entries, showChangeAndBalance = false }: Props = $props();

  let sortedEntries = $state.raw<Entry[]>([]);
  let journalShow = derived(journalShowStore, (t) => new Set(t));

  let head: HTMLLIElement;

  const filter = derived(
    [journalSortOrder, journalShow],
    ([$order, $show]) =>
      [$order, $show] as [JournalSortOrder, Set<JournalShowEntry>],
  );

  let unsub: () => void;
  onMount(() => {
    unsub = filter.subscribe(([journalSortOrder, journalShow]) => {
      let column: SortColumn<Entry>;
      switch (journalSortOrder[0]) {
        case "flag":
          column = new StringColumn("flag", (e) => e.sortFlag);
          break;
        case "narration":
          column = new StringColumn("narration", (e) => e.sortNarration);
          break;
        default:
          column = new DateColumn("date");
          break;
      }
      const sorter = new Sorter(column, journalSortOrder[1] ?? "asc");

      const headers = head.querySelectorAll<HTMLSpanElement>("span[data-sort]");
      headers.forEach((el) => {
        el.removeAttribute("data-order");
        if (el.getAttribute("data-sort-name") === column.name) {
          el.setAttribute("data-order", sorter.order);
        }
      });

      // TODO: remove logging
      console.time("filter");
      const filtered = entries.filter((e) => {
        if (journalShow.has(e.t.toLowerCase() as any)) {
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
              if (e.tags.includes("discovered"))
                return journalShow.has("discovered");
              if (e.tags.includes("linked")) return journalShow.has("linked");
            }
          } else if (e.t === "Custom") {
            if (e.type === "budget") return journalShow.has("budget");
          }
          return true;
        }
        return false;
      });
      console.timeEnd("filter");

      // TODO: remove logging
      console.time("sort");
      const sorted = sorter.sort(filtered);
      console.timeEnd("sort");

      sortedEntries = sorted as Entry[];
    });
  });

  onDestroy(() => unsub());

  function headerClick(e: MouseEvent & { currentTarget: HTMLSpanElement }) {
    const name = e.currentTarget.getAttribute("data-sort-name");
    const order =
      e.currentTarget.getAttribute("data-order") === "asc" ? "desc" : "asc";
    $journalSortOrder = [name as JournalSortOrder[0], order];
  }

  let ol = $state<HTMLDivElement>();
  let lis = $state<HTMLLIElement[]>([]);

  function depend<T, R>(t: T, fn: (t: T) => R) {
    return fn(t);
  }

  let virtualizer = $derived(
    createVirtualizer({
      overscan: 5,
      count: sortedEntries.length,
      getItemKey: depend(
        sortedEntries,
        (sortedEntries) => (i) => sortedEntries[i]?.entry_hash ?? i,
      ),
      getScrollElement: depend(ol, (ol) => () => ol ?? null),
      estimateSize: () => 50,
    }),
  );

  let items = $derived($virtualizer.getVirtualItems());

  $effect(() => {
    if (lis.length) lis.forEach((li) => $virtualizer.measureElement(li));
  });
</script>

<JournalFilters />

<ol class="flex-table journal">
  <li class="head" bind:this={head}>
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

  <div bind:this={ol} class="vlist-outer">
    <div class="vlist-inner" style="height: {$virtualizer.getTotalSize()}px;">
      <div
        class="vlist-items"
        style="transform: translateY({items[0]?.start ?? 0}px);"
      >
        {#each items as row}
          <JournalEntry
            index={row.index}
            e={sortedEntries[row.index]!}
            {showChangeAndBalance}
            journalShow={$journalShow}
            bind:li={lis[row.index]}
          />
        {/each}
      </div>
    </div>
  </div>
</ol>

<style>
  .vlist-outer {
    height: 1000px;
    overflow-y: auto;
    contain: strict;
  }

  .vlist-inner {
    position: relative;
    width: 100%;
  }

  .vlist-items {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
  }
</style>
