<script lang="ts">
  import { onMount } from "svelte";

  import { get_query } from "../../api/index.ts";
  import { err, ok, type Result } from "../../lib/result.ts";
  import { log_error } from "../../log.ts";
  import { router } from "../../router.ts";
  import { filter_params } from "../../stores/filters.ts";
  import { query_shell_history } from "../../stores/query.ts";
  import { searchParams } from "../../stores/url.ts";
  import type { QueryReportProps } from "./index.ts";
  import type { QueryResult } from "./query_table.ts";
  import QueryBox from "./QueryBox.svelte";
  import QueryEditor from "./QueryEditor.svelte";

  let { codemirror_bql }: QueryReportProps = $props();

  /** The current query string in the editor. */
  let query_string = $state.raw("");
  /** The currently loaded results. */
  let results: Record<string, Result<QueryResult, string>> = $state({});
  /** The toggle states of the individual boxes. */
  const is_open: Record<string, boolean> = $state({});

  onMount(() =>
    searchParams.subscribe(($searchParams) => {
      const search_query_string = $searchParams.get("query_string") ?? "";
      // Set the query string to the value from the URL query if that changes (e.g. on navigation).
      if (search_query_string !== query_string) {
        query_string = search_query_string;
        submit();
      }
    }),
  );

  onMount(() =>
    filter_params.subscribe(() => {
      rerun_all_open();
    }),
  );

  /** Submit the current query and load the result for it. */
  function submit() {
    const query = query_string;
    if (!query) {
      return;
    }
    if (query.trim().toUpperCase() === "CLEAR") {
      query_shell_history.clear();
      query_string = "";
      router.set_search_param("query_string", "");
      return;
    }
    query_shell_history.add(query);
    router.set_search_param("query_string", query);
    get_query({ query_string: query, ...$filter_params })
      .then(
        (res) => ok(res),
        (error: unknown) =>
          err(error instanceof Error ? error.message : "INTERNAL ERROR"),
      )
      .then((res) => {
        results[query] = res;
        is_open[query] = true;
        document.querySelector("article")?.scroll(0, 0);
      })
      .catch(log_error);
  }

  /* Re-run all open queries on global filter change. */
  function rerun_all_open() {
    const to_rerun = Object.entries(is_open)
      .filter(([, is_open]) => is_open)
      .map(([query]) => query);
    results = {};
    for (const query of to_rerun) {
      get_query({ query_string: query, ...$filter_params })
        .then(
          (res) => ok(res),
          (error: unknown) =>
            err(error instanceof Error ? error.message : "INTERNAL ERROR"),
        )
        .then((res) => {
          results[query] = res;
        })
        .catch(log_error);
    }
  }

  /** Delete the given query from the history and potentially clear it from the form. */
  function delete_item(query: string) {
    query_shell_history.remove(query);
    if (query_string === query) {
      query_string = "";
      router.set_search_param("query_string", "");
    }
  }
</script>

<QueryEditor bind:value={query_string} {submit} {codemirror_bql} />
{#each $query_shell_history as query (query)}
  <QueryBox
    {query}
    result={results[query]}
    bind:open={is_open[query]}
    onselect={() => {
      query_string = query;
      submit();
    }}
    ondelete={() => {
      delete_item(query);
    }}
    {codemirror_bql}
  />
{/each}
