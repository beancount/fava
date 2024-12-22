<script lang="ts">
  import { onMount } from "svelte";

  import { get } from "../../api";
  import { err, ok, type Result } from "../../lib/result";
  import { log_error } from "../../log";
  import router from "../../router";
  import { filter_params } from "../../stores/filters";
  import { query_shell_history } from "../../stores/query";
  import { searchParams } from "../../stores/url";
  import type { QueryResult } from "./query_table";
  import QueryBox from "./QueryBox.svelte";
  import QueryEditor from "./QueryEditor.svelte";

  let query_string = "";

  /** The currently loaded results. */
  let results: Record<string, Result<QueryResult, string>> = {};
  const is_open: Record<string, boolean> = {};

  onMount(() =>
    searchParams.subscribe((s) => {
      const search_query_string = s.get("query_string") ?? "";
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
    get("query", { query_string: query, ...$filter_params })
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

  /* Re-run all open queries on global filter change */
  function rerun_all_open() {
    const to_rerun = [...Object.entries(is_open)]
      .filter(([, is_open]) => is_open)
      .map(([query]) => query);
    results = {};
    for (const query of to_rerun) {
      get("query", { query_string: query, ...$filter_params })
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

<QueryEditor bind:value={query_string} {submit} />
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
  />
{/each}
