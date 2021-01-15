<script>
  import { onMount, tick } from "svelte";

  import { get } from "../api";
  import { query_shell_history, addToHistory } from "../stores/query";
  import { getFilterParams } from "../stores/filters";
  import { parseQueryChart } from "../charts";

  import Chart from "../charts/Chart.svelte";
  import QueryEditor from "./QueryEditor.svelte";
  import QueryLinks from "./QueryLinks.svelte";

  let query_string = "";

  /** @type {Record<string,HTMLElement>} */
  const resultElems = {};

  /** @typedef {{result?: { table: string, chart: ReturnType<parseQueryChart> }, error?: unknown}} ResultType
  /** @type {Record<string,ResultType>} */
  const query_results = {};

  $: query_result_array = $query_shell_history.map(
    /** @returns {[string, ResultType]} */ (item) => [
      item,
      query_results[item] || {},
    ]
  );

  /**
   * @param {string} query
   * @param {ResultType} res
   */
  async function setResult(query, res) {
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
        const chart = parseQueryChart(res.chart);
        setResult(query, { result: { chart, table: res.table } });
      },
      (error) => {
        setResult(query, { error });
      }
    );
  }

  /**
   * @param {string} query
   */
  function click(query) {
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

<QueryEditor bind:value={query_string} on:submit={submit} />
<div>
  {#each query_result_array as [history_item, { result, error }] (history_item)}
    <details class:error bind:this={resultElems[history_item]}>
      <summary on:click={() => click(history_item)}>
        <pre>
          <code>{history_item}</code>
        </pre>
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
