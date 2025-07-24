<script lang="ts">
  import { VirtualList, type VLSlotSignature } from "svelte-virtuallists";
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
  import { onDestroy } from "svelte";
  import { derived } from "svelte/store";

  interface Props {
    entries: Entry[];
    showChangeAndBalance?: boolean;
  }

  const { entries, showChangeAndBalance = false }: Props = $props();

  let sortedEntries = $state.raw<readonly Entry[]>([]);
  let journalShow = derived(journalShowStore, (t) => new Set(t));

  const filter = derived(
    [journalSortOrder, journalShow],
    ([$order, $show]) =>
      [$order, $show] as [JournalSortOrder, Set<JournalShowEntry>],
  );

  const unsub = filter.subscribe(([journalSortOrder, journalShow]) => {
    let column: SortColumn<Entry>;
    switch (journalSortOrder[0]) {
      case "date":
        column = new DateColumn("date");
        break;
      case "flag":
        column = new StringColumn("flag", (e) => e.sortFlag);
        break;
      case "narration":
        column = new StringColumn("narration", (e) => e.sortNarration);
        break;
    }
    const sorter = new Sorter(column, journalSortOrder[1]);

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

    sortedEntries = sorted;
  });

  onDestroy(() => unsub());
</script>

<JournalFilters />

<ol class="flex-table journal">
  <li class="head">
    <p>
      <span
        class="datecell"
        data-sort="num"
        data-sort-name="date"
        data-order="asc"
      >
        {_("Date")}
      </span>
      <span class="flag" data-sort="string" data-sort-name="flag">
        {_("F")}
      </span>
      <span class="description" data-sort="string" data-sort-name="narration">
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
  <VirtualList items={sortedEntries as Entry[]} style="height: 100vh;">
    {#snippet vl_slot({ item, index }: VLSlotSignature<Entry>)}
      <JournalEntry
        index={+index + 1}
        entry={item}
        {showChangeAndBalance}
        journalShow={$journalShow}
      />
    {/snippet}
  </VirtualList>
</ol>
