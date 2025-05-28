<script lang="ts">
  import type { Document } from "../../entries";
  import { _ } from "../../i18n";
  import { is_descendant_or_equal } from "../../lib/account";
  import { basename } from "../../lib/paths";
  import { DateColumn, Sorter, StringColumn } from "../../sort";
  import SortHeader from "../../sort/SortHeader.svelte";
  import { selectedAccount } from "./stores";

  interface Props {
    data: Document[];
    selected?: Document | null;
  }

  let { data, selected = $bindable(null) }: Props = $props();

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
  let sorter = $state(new Sorter(columns[0], "desc"));

  let is_descendant_of_selected = $derived(
    is_descendant_or_equal($selectedAccount),
  );
  let filtered_documents = $derived(
    data.filter((doc) => is_descendant_of_selected(doc.account)),
  );
  let sorted_documents = $derived(sorter.sort(filtered_documents));
</script>

<table>
  <thead>
    <tr>
      {#each columns as column (column)}
        <SortHeader bind:sorter {column} />
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each sorted_documents as doc (doc.filename)}
      <tr
        class:selected={selected === doc}
        draggable={true}
        title={doc.filename}
        ondragstart={(ev) => {
          ev.dataTransfer?.setData("fava/filename", doc.filename);
        }}
        onclick={() => {
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
