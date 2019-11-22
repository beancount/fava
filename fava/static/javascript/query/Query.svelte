<script>
  import { onMount } from "svelte";

  import { fetchAPI } from "../helpers";
  import { query_shell_history, addToHistory } from "../stores/query";
  import { parseQueryChart } from "../charts";

  import Chart from "../charts/Chart.svelte";
  import QueryEditor from "./QueryEditor.svelte";
  import QueryLinks from "./QueryLinks.svelte";

  let query_string = "";

  const query_results = {};

  $: query_result_array = $query_shell_history.map(item => {
    return [item, query_results[item] || {}];
  });

  function submit() {
    const query = query_string;
    fetchAPI("query_result", { query_string: query }).then(
      result => {
        addToHistory(query);
        result.chart = parseQueryChart(result.chart);
        query_results[query] = { result };
        const url = new URL(window.location.toString());
        url.searchParams.set("query_string", query);
        window.history.replaceState(null, "", url.toString());
        // TODO: initSort();
      },
      error => {
        addToHistory(query);
        query_results[query] = { error };
      }
    );
  }

  function click(query) {
    if (!query_results[query]) {
      query_string = query;
      submit();
    }
  }

  onMount(() => {
    const url = new URL(window.location);
    query_string = url.searchParams.get("query_string") || "";
    if (query_string) {
      submit();
    }
  });
</script>

<QueryEditor bind:value={query_string} on:submit={submit} />
<div>
  {#each query_result_array as [history_item, { result, error }] (history_item)}
    <details class="query-result" class:error>
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
