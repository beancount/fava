<script lang="ts">
  import { onMount, tick } from "svelte";

  import { get } from "../api";
  import { parseQueryChart } from "../charts";
  import Chart from "../charts/Chart.svelte";
  import { operatingCurrenciesWithConversion } from "../stores";
  import { getFilterParams } from "../stores/filters";
  import { addToHistory, query_shell_history } from "../stores/query";

  import QueryEditor from "./QueryEditor.svelte";
  import QueryLinks from "./QueryLinks.svelte";
  import ReadonlyQueryEditor from "./ReadonlyQueryEditor.svelte";

  let query_string = "";

  const resultElems: Record<string, HTMLElement> = {};

  type ResultType = {
    result?: { table: string; chart: ReturnType<typeof parseQueryChart> };
    error?: unknown;
  };

  const query_results: Record<string, ResultType> = {};

  $: query_result_array = $query_shell_history.map((item): [
    string,
    ResultType
  ] => [item, query_results[item] || {}]);

  async function setResult(query: string, res: ResultType) {
    addToHistory(query);
    query_results[query] = res;
    await tick();
    const url = new URL(window.location.href);
    url.searchParams.set("query_string", query);
    window.history.replaceState(null, "", url.toString());
    resultElems[query].setAttribute("open", "true");
  }

  function submit() {
    const query = query_string;
    if (!query) {
      return;
    }
    get("query_result", { query_string: query, ...getFilterParams() }).then(
      (res) => {
        const chart = parseQueryChart(
          res.chart,
          $operatingCurrenciesWithConversion
        );
        setResult(query, { result: { chart, table: res.table } });
      },
      (error) => {
        setResult(query, { error });
      }
    );
  }

  function click(query: string) {
    if (!query_results[query]) {
      query_string = query;
      submit();
    }
  }

  onMount(() => {
    const url = new URL(window.location.href);
    query_string = url.searchParams.get("query_string") || "";
    if (query_string) {
      submit();
    }
  });
</script>

<QueryEditor bind:value={query_string} {submit} />
<div>
  {#each query_result_array as [history_item, { result, error }] (history_item)}
    <details class:error bind:this={resultElems[history_item]}>
      <summary on:click={() => click(history_item)}>
        <ReadonlyQueryEditor value={history_item} />
        {#if result}
          <span class="spacer" />
          <QueryLinks query={history_item} />
        {/if}
      </summary>
      <div>
        {#if result}
          {#if result.chart}
            <Chart chart={result.chart} />
          {/if}
          {@html result.table}
        {:else if error}
          {@html error}
        {/if}
      </div>
    </details>
  {/each}
</div>

<style>
  details > div {
    max-height: 80vh;
    overflow: auto;
  }

  div :global(.query-error) {
    font-family: var(--font-family-monospaced);
    color: var(--color-background);
    background: var(--color-error);
  }
</style>
