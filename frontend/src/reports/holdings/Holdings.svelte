<script lang="ts">
  import { url_for } from "../../helpers.ts";
  import { _ } from "../../i18n.ts";
  import QueryLinks from "../query/QueryLinks.svelte";
  import QueryTable from "../query/QueryTable.svelte";
  import type { HoldingsReportProps } from "./index.ts";

  let {
    aggregation_key,
    query_string,
    query_result_table,
  }: HoldingsReportProps = $props();
</script>

<div class="headerline">
  <h3>
    {#if aggregation_key === "all"}
      {_("Holdings")}
    {:else}
      <a href={$url_for("holdings/")}>{_("Holdings")}</a>
    {/if}
  </h3>
  <h3>
    {#if aggregation_key === "by_account"}
      {_("Holdings by")} {_("Account")}
    {:else}
      <a href={$url_for("holdings/by_account/")}>
        {_("Holdings by")}
        {_("Account")}
      </a>
    {/if}
  </h3>
  <h3>
    {#if aggregation_key === "by_currency"}
      {_("Holdings by")} {_("Currency")}
    {:else}
      <a href={$url_for("holdings/by_currency/")}>
        {_("Holdings by")}
        {_("Currency")}
      </a>
    {/if}
  </h3>
  <h3>
    {#if aggregation_key === "by_cost_currency"}
      {_("Holdings by")} {_("Cost currency")}
    {:else}
      <a href={$url_for("holdings/by_cost_currency/")}>
        {_("Holdings by")}
        {_("Cost currency")}
      </a>
    {/if}
  </h3>
</div>

<p>
  <a href={$url_for("query/", { query_string })}>{_("Query")}</a>
  <QueryLinks query={query_string} />
</p>
<QueryTable table={query_result_table} filter_empty="units" />
