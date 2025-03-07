<script lang="ts">
  import { urlFor } from "../../helpers";
  import { _ } from "../../i18n";
  import QueryLinks from "../query/QueryLinks.svelte";
  import QueryTable from "../query/QueryTable.svelte";
  import type { HoldingsReportProps } from ".";

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
      <a href={$urlFor("holdings/")}>{_("Holdings")}</a>
    {/if}
  </h3>
  <h3>
    {#if aggregation_key === "by_account"}
      {_("Holdings by")} {_("Account")}
    {:else}
      <a href={$urlFor("holdings/by_account/")}>
        {_("Holdings by")}
        {_("Account")}
      </a>
    {/if}
  </h3>
  <h3>
    {#if aggregation_key === "by_currency"}
      {_("Holdings by")} {_("Currency")}
    {:else}
      <a href={$urlFor("holdings/by_currency/")}>
        {_("Holdings by")}
        {_("Currency")}
      </a>
    {/if}
  </h3>
  <h3>
    {#if aggregation_key === "by_cost_currency"}
      {_("Holdings by")} {_("Cost currency")}
    {:else}
      <a href={$urlFor("holdings/by_cost_currency/")}>
        {_("Holdings by")}
        {_("Cost currency")}
      </a>
    {/if}
  </h3>
</div>

<p>
  <a href={$urlFor("query", { query_string })}>{_("Query")}</a>
  <QueryLinks query={query_string} />
</p>
<QueryTable table={query_result_table} filter_empty="units" />
