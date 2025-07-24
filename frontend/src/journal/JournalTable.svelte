<script lang="ts">
  import { VirtualList, type VLSlotSignature } from "svelte-virtuallists";
  import type { Entry } from "../entries";
  import { _ } from "../i18n";
  import JournalEntry from "./JournalEntry.svelte";

  interface Props {
    entries: Entry[];
    showChangeAndBalance?: boolean;
  }

  const { entries, showChangeAndBalance = false }: Props = $props();
</script>

<fava-journal>
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
    <VirtualList items={entries} style="height: 1000px;">
      {#snippet vl_slot({ item, index }: VLSlotSignature<Entry>)}
        <JournalEntry index={+index + 1} entry={item} {showChangeAndBalance} />
      {/snippet}
    </VirtualList>
  </ol>
</fava-journal>
