<script lang="ts">
  import { onMount, tick } from "svelte";

  import { get } from "../../api";
  import type { FavaChart } from "../../charts";
  import Chart from "../../charts/Chart.svelte";
  import { chartContext } from "../../charts/context";
  import { parseQueryChart } from "../../charts/query-charts";
  import { log_error } from "../../log";
  import router from "../../router";
  import { filter_params } from "../../stores/filters";
  import {
    addToHistory,
    clearHistory,
    query_shell_history,
  } from "../../stores/query";

  import QueryEditor from "./QueryEditor.svelte";
  import QueryLinks from "./QueryLinks.svelte";
  import ReadonlyQueryEditor from "./ReadonlyQueryEditor.svelte";

  let query_string = "";

  const resultElems: Record<string, HTMLElement> = {};

  interface ResultType {
    result?: { table: string; chart: FavaChart | null };
    error?: unknown;
  }

  const query_results: Record<string, ResultType> = {};

  $: query_result_array = $query_shell_history.map(
    (item): [string, ResultType] => [item, query_results[item] ?? {}]
  );

  async function setResult(query: string, res: ResultType) {
    addToHistory(query);
    query_results[query] = res;
    await tick();
    const url = new URL(window.location.href);
    url.searchParams.set("query_string", query);
    window.history.replaceState(null, "", url.toString());
    resultElems[query]?.setAttribute("open", "true");
  }

  async function clearResults() {
    clearHistory();
    await tick();
    const url = new URL(window.location.href);
    query_string = "";
    url.searchParams.set("query_string", query_string);
    window.history.replaceState(null, "", url.toString());
  }

  function submit() {
    const query = query_string;
    if (!query) {
      return;
    }
    if (query.trim().toUpperCase() === "CLEAR") {
      clearResults().catch(log_error);
      return;
    }
    get("query_result", { query_string: query, ...$filter_params }).then(
      (res) => {
        const r = parseQueryChart(res.chart, $chartContext);
        const chart = r.success ? r.value : null;
        setResult(query, { result: { chart, table: res.table } }).catch(
          log_error
        );
        window.scroll(0, 0);
      },
      (error) => {
        if (error instanceof Error) {
          setResult(query, { error: error.message }).catch(log_error);
          window.scroll(0, 0);
        } else {
          setResult(query, {
            error: "Received invalid data as query error.",
          }).catch(log_error);
        }
      }
    );
  }

  function click(query: string) {
    if (!query_results[query]) {
      query_string = query;
      submit();
    }
  }

  onMount(() =>
    router.on("page-loaded", () => {
      const url = new URL(window.location.href);
      query_string = url.searchParams.get("query_string") ?? "";
      if (query_string) {
        submit();
      }
    })
  );
</script>

<QueryEditor bind:value={query_string} {submit} />
<div>
  {#each query_result_array as [history_item, { result, error }] (history_item)}
    <details bind:this={resultElems[history_item]}>
      <summary
        class:inactive={!result && !error}
        on:click={() => click(history_item)}
      >
        <ReadonlyQueryEditor value={history_item} error={!!error} />
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
          <!-- eslint-disable-next-line svelte/no-at-html-tags -->
          {@html result.table}
        {:else if error}
          <pre>{error}</pre>
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

  .inactive {
    filter: opacity(0.5);
  }

  div :global(.query-error) {
    font-family: var(--font-family-monospaced);
    color: var(--background);
    background: var(--error);
  }
</style>