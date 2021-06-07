<script lang="ts">
  import { _ } from "../i18n";
  import { isDescendant } from "../lib/account";
  import { basename } from "../lib/paths";
  import { sortFunc } from "../sort";

  import { selectedAccount } from "./stores";
  import type { Document } from "./types";

  export let data: Document[];
  export let selected: Document | null = null;

  /**
   * Extract just the latter part of the filename if it starts with a date.
   */
  function name(doc: Document) {
    const base = basename(doc.filename);
    return `${doc.date}` === base.substring(0, 10) ? base.substring(11) : base;
  }

  const headers: [string, string] = [_("Date"), _("Name")];
  const rowGetter: (d: Document) => [string, string] = (d) => [d.date, name(d)];

  /** Index of the table column that is sorted by. */
  let sortColumn = 0;
  /** Sort order. */
  let sortOrder: "asc" | "desc" = "desc";

  $: table = data
    .filter((doc) => isDescendant(doc.account, $selectedAccount))
    .map((doc) => ({ doc, row: rowGetter(doc) }));
  $: sortedTable = table.sort(
    sortFunc("string", sortOrder, ({ row }) => row[sortColumn])
  );

  function setSort(index: number) {
    if (index === sortColumn) {
      sortOrder = sortOrder === "asc" ? "desc" : "asc";
    } else {
      sortOrder = "asc";
      sortColumn = index;
    }
  }
</script>

<table>
  <thead>
    <tr>
      {#each headers as header, index}
        <th
          on:click={() => setSort(index)}
          data-sort
          data-order={index === sortColumn ? sortOrder : null}
        >
          {header}
        </th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each sortedTable as { doc, row }}
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
        <td>{row[0]}</td>
        <td>{row[1]}</td>
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
    background-color: var(--color-table-header-background);
  }
</style>
