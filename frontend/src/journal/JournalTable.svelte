<script lang="ts">
  import { createVirtualizer } from "@tanstack/svelte-virtual";
  import { onDestroy, onMount, tick, type Snippet } from "svelte";
  import { derived, writable } from "svelte/store";

  import type { Entry } from "../entries";
  import { _ } from "../i18n";
  import { Sorter, StringColumn } from "../sort";
  import {
    journalShow as journalShowStore,
    type JournalShowEntry,
    type JournalSortOrder,
    journalSortOrder,
  } from "../stores/journal";
  import JournalEntry from "./JournalEntry.svelte";
  import JournalFilters from "./JournalFilters.svelte";
  import type { AccountJournalEntry } from "../api/validators";
  import Header from "../sidebar/Header.svelte";
  import { hideHeader } from "../stores";

  type E = Entry | AccountJournalEntry;
  interface Props {
    entries: E[];
    showChangeAndBalance?: boolean;
    header?: Snippet;
  }

  const {
    entries: entriesProp,
    showChangeAndBalance = false,
    header,
  }: Props = $props();

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

  // Use manual stores as using $derived is slow here.
  const entries = writable(entriesProp);
  const journalShow = derived(journalShowStore, (t) => new Set(t));
  const filter = derived([journalSortOrder, journalShow, entries], (it) => it);
  const unsub = filter.subscribe(
    ([[sortColumn, sortOrder], journalShow, entries]) => {
      let column: (e: Entry) => string;
      switch (sortColumn) {
        case "flag":
          column = (e) => e.sortFlag;
          break;
        case "narration":
          column = (e) => e.sortNarration;
          break;
        default:
          column = (e) => e.date;
          break;
      }
      const sorter = new Sorter<E>(
        new StringColumn(
          "",
          (e, i, a) => column(entry(e)) + i.toString().padStart(a.length, "0"),
        ),
        sortOrder ?? "asc",
      );

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
    },
  );

  // Update the manual store when the prop update.
  $effect(() => entries.set(entriesProp));
  onDestroy(() => unsub());

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

  let mobileHeader = $state(false);
  onMount(() => {
    const mediaQuery = window.matchMedia("(width <= 767px)");
    const onChange = () => {
      // Wait for update tick so keyboard shortcut not duplicated.
      if (mediaQuery.matches) {
        $hideHeader = true;
        tick().then(() => mobileHeader = true);
      } else {
        mobileHeader = false;
        tick().then(() => $hideHeader = false);
      }
    };

    mediaQuery.addEventListener("change", onChange);
    onChange();

    onDestroy(() => {
      $hideHeader = false;
      mediaQuery.removeEventListener("change", onChange);
    });
  });
</script>

<div class="fixed-fullsize-container">
  <div bind:this={vlistOuter} class="vlist-outer">
    <div
      class="flex-table vlist-inner"
      style="height: {$virtualizer.getTotalSize()}px;"
    >
      <ol
        class="vlist-items journal"
        style="transform: translateY({items[0]?.start ?? 0}px);"
      >
        {#each items as row (row.index)}
          {#if row.index === 0}
            <li class="head" bind:this={head} data-index="0">
              {#if mobileHeader}
                <div class="header-mobile">
                  <Header />
                </div>
              {/if}
              <div class="container">
                {@render header?.()}
                <JournalFilters />
              </div>
              <div class="table-head">
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
              </div>
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
  .vlist-outer {
    height: 100%;
    /* padding: 1.5em; */
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

  .head > .container {
    padding: 1.5em 1.5em 0 1.5em;
    margin-bottom: 0.25em;
  }

  .head .table-head {
    padding: 0 1.5em;
  }

  @media (width <= 767px) {
    .head > .container {
      padding: 1em 1em 0 1em;
    }

    .head .table-head {
      padding: 0 1em;
    }
  }
</style>
