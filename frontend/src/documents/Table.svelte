<script>
  import { sortFunc } from "../sort";
  import { _ } from "../i18n";

  import { selectedAccount } from "./stores";
  import { basename } from "../lib/paths";

  /** @typedef {{account: string, filename: string, date: string}} Document */

  /** @type {Document[]} */
  export let data;
  /** @type {Document | null} */
  export let selected = null;

  /**
   * Extract just the latter part of the filename if it starts with a date.
   * @param {Document} doc
   */
  function name(doc) {
    const base = basename(doc.filename);
    if (`${doc.date}` === base.substring(0, 10)) {
      return base.substring(11);
    }
    return base;
  }

  const tableColumns = [
    {
      header: _("Date"),
      getter: (/** @type {Document} */ e) => e.date,
    },
    {
      header: _("Name"),
      getter: (/** @type {Document} */ e) => name(e),
    },
  ];

  /**
   * Index of the table column and order to sort by
   * @type {[number, "asc" | "desc"]}
   */
  let sort = [0, "desc"];
  $: table = data
    .filter((e) => e.account.startsWith($selectedAccount))
    .map((e) => ({ doc: e, row: tableColumns.map((th) => th.getter(e)) }))
    .sort(sortFunc("string", sort[1], ({ row }) => row[sort[0]]));

  /**
   * @param {number} index
   */
  function setSort(index) {
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
