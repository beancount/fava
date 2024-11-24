<!--
  @component
  Renders a query result in a collapsible box.
-->
<svelte:options immutable />

<script lang="ts">
  import Chart from "../../charts/Chart.svelte";
  import { chartContext } from "../../charts/context";
  import { getQueryChart } from "../../charts/query-charts";
  import type { Result } from "../../lib/result";
  import type { QueryResult } from "./query_table";
  import QueryLinks from "./QueryLinks.svelte";
  import QueryTable from "./QueryTable.svelte";
  import ReadonlyQueryEditor from "./ReadonlyQueryEditor.svelte";

  /** The query string. */
  export let query: string;
  /** The query result, possibly missing or an error. */
  export let result: Result<QueryResult, string> | undefined;
  /** Whether this box is open. */
  export let open: boolean | undefined;

  /** Handler to run on 'select' (clicking the summary bar). */
  export let onselect: () => void;
  /** Handler to run on 'delete' (clicking the x button). */
  export let ondelete: () => void;

  $: inactive = !result;
  $: chart =
    result && result.is_ok && result.value.t === "table"
      ? getQueryChart(result.value, $chartContext)
      : null;
</script>

<details bind:open>
  <summary class:inactive on:click={inactive ? onselect : null}>
    <ReadonlyQueryEditor value={query} error={result?.is_err} />
    <span class="spacer"></span>
    {#if result && result.is_ok && result.value.t === "table"}
      <QueryLinks {query} />
    {/if}
    <button
      type="button"
      on:click={(ev) => {
        ev.stopPropagation();
        ondelete();
      }}
    >
      x
    </button>
  </summary>
  <div>
    {#if result}
      {#if result.is_ok}
        {#if result.value.t === "string"}
          <pre><code>{result.value.contents}</code></pre>
        {:else}
          {#if chart}
            <Chart {chart} />
          {/if}
          <QueryTable table={result.value} />
        {/if}
      {:else}
        <pre><code>{result.error}</code></pre>
      {/if}
    {/if}
  </div>
</details>

<style>
  details > div {
    max-height: 70vh;
    overflow: auto;
  }

  .inactive {
    filter: opacity(0.5);
  }

  pre {
    margin: 0;
  }
</style>
