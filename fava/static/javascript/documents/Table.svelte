<script>
  import { sortFunc } from "../sort";
  import { _ } from "../helpers";

  import { selectedAccount } from "./stores";
  import { basename } from "./util";

  export let data;
  export let selected;

  /* Extract just the latter part of the filename if it starts with a date. */
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
      getter: e => e.date,
    },
    {
      header: _("Name"),
      getter: e => name(e),
    },
  ];

  /** Index of the table column and order to sort by */
  let sort = [0, "desc"];
  $: table = data
    .filter(e => e.account.startsWith($selectedAccount))
    .map(e => [e, tableColumns.map(th => th.getter(e))])
    .sort(sortFunc("string", sort[1], row => row[1][sort[0]]));

  function setSort(index) {
    const [col, order] = sort;
    if (index === col) {
      sort = [index, order === "asc" ? "desc" : "asc"];
    } else {
      sort = [index, "asc"];
    }
  }
</script>

<style>
  tr {
    cursor: pointer;
  }
  .selected,
  tr:hover {
    background-color: var(--color-table-header-background);
  }
</style>

<table style="width: 100%">
  <thead>
    <tr>
      {#each tableColumns as col, index}
        <th
          on:click={() => setSort(index)}
          data-sort
          data-order={index === sort[0] ? sort[1] : null}>
          {col.header}
        </th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each table as [doc, row]}
      <tr
        class:selected={selected === doc}
        draggable="true"
        title={doc.filename}
        on:dragstart={ev => {
          ev.dataTransfer.setData('fava/filename', doc.filename);
        }}
        on:click={() => {
          selected = doc;
        }}>
        <td>{row[0]}</td>
        <td>{row[1]}</td>
      </tr>
    {/each}
  </tbody>
</table>
