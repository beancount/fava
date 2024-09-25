<script lang="ts">
  import type { Document } from "../../entries";
  import { _ } from "../../i18n";
  import { isDescendant } from "../../lib/account";
  import { basename } from "../../lib/paths";
  import { DateColumn, Sorter, StringColumn } from "../../sort";
  import SortHeader from "../../sort/SortHeader.svelte";
  import { selectedAccount } from "./stores";

  export let data: Document[];
  export let selected: Document | null = null;

  /**
   * Extract just the latter part of the filename if it starts with a date.
   */
  function name(doc: Document) {
    const base = basename(doc.filename);
    return base.startsWith(doc.date) ? base.substring(11) : base;
  }

  const columns = [
    new DateColumn<Document>(_("Date")),
    new StringColumn<Document>(_("Name"), (d) => name(d)),
  ] as const;
  let sorter = new Sorter(columns[0], "desc");

  $: filtered_documents = data.filter((doc) =>
    isDescendant(doc.account, $selectedAccount),
  );
  $: sorted_documents = sorter.sort(filtered_documents);
</script>

<table>
  <thead>
    <tr>
      {#each columns as column}
        <SortHeader bind:sorter {column} />
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each sorted_documents as doc}
      <tr
        class:selected={selected === doc}
        draggable={true}
        title={doc.filename}
        on:dragstart={(ev) => {
          ev.dataTransfer?.setData("fava/filename", doc.filename);
        }}
        on:click={() => {
          selected = doc;
        }}
      >
        <td>{doc.date}</td>
        <td>{name(doc)}</td>
      </tr>
    {/each}
  </tbody>
</table>

<style>
  table {
    width: 100%;
  }

  tr {
    cursor: pointer;
  }

  .selected,
  tr:hover {
    background-color: var(--table-header-background);
  }
</style>
