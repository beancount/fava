<script lang="ts">
  import { urlFor } from "../helpers";
  import { _ } from "../i18n";
  import { keyboardShortcut } from "../keyboard-shortcuts";
  import { errors, extensions, ledgerData } from "../stores";
  import AccountSelector from "./AccountSelector.svelte";
  import Link from "./SidebarLink.svelte";
  import { onMount } from "svelte";
  import TodayBalanceModal from "../modals/TodayBalanceModal.svelte";

  let showModal = $state(false); // 使用 $state 来确保 showModal 是响应式的
  let balance = $state("Loading...");
  const { onClose } = $props();

  const showAccountOverviewInNewWindow = async () => {
    try {
      const pathParts = window.location.pathname.split("/");
      const bfile = pathParts.length > 1 ? pathParts[1] : "";
      const res = await fetch(`/${bfile}/api/account_overview`);
      const { data } = await res.json();

      const tableRows = data
        .map(
          (row: any, index: number) => `
        <tr class="${index % 2 === 0 ? "even" : "odd"}">
          <td class="account">${row.account}</td>
          <td class="date">${row.last_posting_date}</td>
          <td class="balance">${row.balance} ${row.currency}</td>
        </tr>`,
        )
        .join("");

      const newWindow = window.open("", "_blank", "width=950,height=600");
      newWindow?.document.write(`
      <html>
        <head>
          <title>账户总览</title>
          <style>
            body {
              font-family: 'Segoe UI', Roboto, sans-serif;
              background: #f9f9fb;
              margin: 0;
              padding: 2rem;
              color: #333;
            }

            h1 {
              font-size: 1.6rem;
              margin-bottom: 1rem;
              text-align: center;
              color: #007acc;
            }

            table {
              width: 100%;
              border-collapse: collapse;
              box-shadow: 0 0 8px rgba(0, 0, 0, 0.05);
              background: white;
              border-radius: 8px;
              overflow: hidden;
            }

            thead {
              background-color: #e9f4fc;
            }

            th {
              text-align: left;
              padding: 0.75rem 1rem;
              font-weight: 600;
              border-bottom: 2px solid #ccc;
              color: #007acc;
            }

            td {
              padding: 0.6rem 1rem;
              border-bottom: 1px solid #eee;
              vertical-align: middle;
            }

            tr.even {
              background-color: #fcfcfc;
            }

            tr.odd {
              background-color: #f5f9fc;
            }

            td.balance {
              text-align: right;
              font-family: monospace;
              font-weight: bold;
              color: #333;
            }

            td.date {
              white-space: nowrap;
              color: #666;
            }

            td.account {
              font-family: monospace;
              color: #333;
            }
          </style>
        </head>
        <body>
          <h1>账户总览</h1>
          <table>
            <thead>
              <tr>
                <th>账户</th>
                <th>最新条目</th>
                <th>余额</th>
              </tr>
            </thead>
            <tbody>
              ${tableRows}
            </tbody>
          </table>
        </body>
      </html>
    `);

      newWindow?.document.close();
    } catch (e) {
      console.error("Error fetching account overview", e);
    }
  };

  const truncate = (s: string) => (s.length < 25 ? s : `${s.slice(25)}…`);

  let user_queries = $derived($ledgerData.user_queries);
  let upcoming_events_count = $derived($ledgerData.upcoming_events_count);
  let sidebar_links = $derived($ledgerData.sidebar_links);
  let extension_reports = $derived(
    $extensions.filter((e) => e.report_title != null),
  );
</script>

{#if sidebar_links.length}
  <ul class="navigation">
    {#each sidebar_links as [label, link]}
      <Link report={link} name={label} remote />
    {/each}
  </ul>
{/if}
<ul class="navigation">
  <Link report="income_statement" name={_("Income Statement")} key="g i" />
  <Link report="balance_sheet" name={_("Balance Sheet")} key="g b" />
  <Link report="trial_balance" name={_("Trial Balance")} key="g t" />
  <Link report="journal" name={_("Journal")} key="g j" />
  <Link report="query" name={_("Query")} key="g q">
    {#if user_queries.length}
      <ul class="submenu">
        {#each user_queries as { query_string, name }}
          <li>
            <a href={$urlFor("query/", { query_string })}>{truncate(name)}</a>
          </li>
        {/each}
      </ul>
    {/if}
  </Link>
  <AccountSelector />
</ul>
<ul class="navigation">
  <Link report="holdings" name={_("Holdings")} key="g h" />
  <Link report="commodities" name={_("Commodities")} key="g c" />
  <Link report="documents" name={_("Documents")} key="g d" />
  <Link
    report="events"
    name={_("Events")}
    key="g E"
    bubble={[upcoming_events_count, "info"]}
  />
  <Link report="statistics" name={_("Statistics")} key="g s" />
  <li>
    <button
      onclick={showAccountOverviewInNewWindow}
      style="width:100%;padding:0.25em 0.5em 0.25em 1em;
           font:inherit;color:inherit;text-align:left;cursor:pointer;background:none;border:none;"
    >
      📋 账户总览
    </button>
  </li>
</ul>
<ul class="navigation">
  <Link report="editor" name={_("Editor")} key="g e">
    <a
      href="#add-transaction"
      class="secondary add-transaction"
      title={_("Add Journal Entry")}
      use:keyboardShortcut={"n"}>+</a
    >
  </Link>
  {#if $errors.length > 0}
    <Link
      report="errors"
      name={_("Errors")}
      bubble={[$errors.length, "error"]}
    />
  {/if}
  <Link report="import" name={_("Import")} key="g n">
    <a href="#export" class="secondary" title={_("Export")}>⬇</a>
  </Link>
  <Link report="options" name={_("Options")} key="g o" />
  <Link report="help" name={_("Help")} key="g H" />
</ul>
{#if extension_reports.length}
  <ul class="navigation">
    {#each extension_reports as ext}
      <Link report={`extension/${ext.name}`} name={ext.report_title ?? ""} />
    {/each}
  </ul>
{/if}

{#if showModal}
  <TodayBalanceModal {onClose} {balance} />
{/if}

<style>
  .navigation {
    padding-bottom: 0.5rem;
    margin: 0;
  }

  .navigation + .navigation {
    padding-top: 0.5rem;
    border-top: 1px solid var(--sidebar-border);
  }

  a {
    display: block;
    padding: 0.25em 0.5em 0.25em 1em;
    color: inherit;
  }

  a:hover {
    color: var(--sidebar-hover-color);
    background-color: var(--sidebar-border);
  }

  .secondary {
    width: 30px;
    padding: 3px 9px;
    line-height: 22px;
    color: inherit;
    background-color: var(--sidebar-background);
  }

  .add-transaction {
    font-size: 23px;
  }

  .submenu {
    width: 100%;
    margin: 0 0 0.5em;
  }

  .submenu a {
    width: 100%;
    padding-left: 35px;
  }

  .submenu li {
    font-size: 0.9em;
  }
</style>
