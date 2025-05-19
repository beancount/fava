<script lang="ts">
  import { urlFor } from "../helpers";
  import { _ } from "../i18n";
  import { keyboardShortcut } from "../keyboard-shortcuts";
  import { errors, extensions, ledgerData } from "../stores";
  import AccountSelector from "./AccountSelector.svelte";
  import Link from "./SidebarLink.svelte";
  import { onMount } from "svelte";
  import TodayBalanceModal from "../modals/TodayBalanceModal.svelte";

  let showModal = $state(false);  // 使用 $state 来确保 showModal 是响应式的
  let balance = $state("Loading...");
  const { onClose } = $props();

  // 在组件挂载时发起 API 请求
  onMount(async () => {
    try {
      const res = await fetch("/api/today_balance");
      const data = await res.json();
      balance = `${data.balance} USD`;  // 更新 balance
    } catch (e) {
      balance = "Error fetching data";  // 错误时显示信息
    }
  });
  const showBalanceInNewWindow = async () => {
    try {
      const res = await fetch("/api/today_balance");
      const data = await res.json();  // 解包 JSON 数据

      // 尝试打开一个新窗口
      const newWindow = window.open("", "_blank", "width=600,height=400");

      // 确保 newWindow 被正确打开
      if (newWindow) {
        newWindow.document.write("<h1>Today's Balance</h1>");
        newWindow.document.write("<pre>" + JSON.stringify(data, null, 2) + "</pre>");
      } else {
        console.error("Unable to open new window.");
      }
    } catch (e) {
      console.error("Error fetching data", e);
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
<!-- <li>
  <button onclick={() => (showModal = true)} style="background:none;border:none;padding:0.25em 0.5em 0.25em 1em;font:inherit;cursor:pointer;color:inherit;width:100%;text-align:left;">
    📊 今日余额
  </button>
</li> -->
<!-- 触发 showBalanceInNewWindow 显示今日余额的按钮 -->
<li>
  <button onclick={showBalanceInNewWindow} style="background:none;border:none;padding:0.25em 0.5em 0.25em 1em;font:inherit;cursor:pointer;color:inherit;width:100%;text-align:left;">
    📊 显示今日余额 (新窗口)
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
  <TodayBalanceModal {onClose} balance={balance} />
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
