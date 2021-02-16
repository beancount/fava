<script lang="ts">
  import { _ } from "../i18n";
  import { basename } from "../lib/paths";
  import { sortFunc } from "../sort";

  import { selectedAccount } from "./stores";

  type Document = { account: string; filename: string; date: string };

  export let data: Document[];
  export let selected: Document | null = null;

  /**
   * Extract just the latter part of the filename if it starts with a date.
   */
  function name(doc: Document) {
    const base = basename(doc.filename);
    if (`${doc.date}` === base.substring(0, 10)) {
      return base.substring(11);
    }
    return base;
  }

  const tableColumns: { header: string; getter: (e: Document) => string }[] = [
    {
      header: _("Date"),
      getter: (e) => e.date,
    },
    {
      header: _("Name"),
      getter: (e) => name(e),
    },
  ];

  /**
   * Index of the table column and order to sort by.
   */
  let sort: [number, "asc" | "desc"] = [0, "desc"];
  $: table = data
    .filter((e) => e.account.startsWith($selectedAccount))
    .map((e) => ({ doc: e, row: tableColumns.map((th) => th.getter(e)) }))
    .sort(sortFunc("string", sort[1], ({ row }) => row[sort[0]]));

  function setSort(index: number) {
    const [col, order] = sort;
    if (index === col) {
      sort = [index, order === "asc" ? "desc" : "asc"];
    } else {
      sort = [index, "asc"];
    }
  }
</script>

<table>
  <thead>
    <tr>
      {#each tableColumns as col, index}
        <th
          on:click={() => setSort(index)}
          data-sort
          data-order={index === sort[0] ? sort[1] : null}
        >
          {col.header}
        </th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each table as { doc, row }}
      <tr
        class:selected={selected === doc}
        draggable={true}
        title={doc.filename}
        on:dragstart={(ev) =>
          ev.dataTransfer?.setData("fava/filename", doc.filename)}
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
