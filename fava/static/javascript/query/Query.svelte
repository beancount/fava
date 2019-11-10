<script context="module">
  import { writable } from "svelte/store";

  const stored_history_string = localStorage.getItem("fava-query-history");
  let initialList = [];
  if (stored_history_string) {
    initialList = JSON.parse(stored_history_string);
  }
  const query_shell_history = writable(initialList);
  query_shell_history.subscribe(val => {
    if (val.length) {
      localStorage.setItem("fava-query-history", JSON.stringify(val));
    }
  });

  function addToHistory(query) {
    if (query) {
      query_shell_history.update(hist => {
        hist.unshift(query);
        return [...new Set(hist)];
      });
    }
  }
</script>

<script>
  import CodeMirror from "codemirror";
  import { onMount } from "svelte";

  import { ignoreKey } from "../editor";
  import { _, fetchAPI, urlFor } from "../helpers";
  import { favaAPIStore } from "../stores";

  let query_string = "";
  let form;
  let editor;

  const query_results = {};

  $: query_result_array = $query_shell_history.map(item => {
    return [item, query_results[item] || {}];
  });

  function submit(query) {
    const url = new URL(window.location.toString());
    url.searchParams.set("query_string", query);
    if (editor) {
      editor.setValue(query);
    }
    const pageURL = url.toString();

    fetchAPI("query_result", { query_string: query }).then(
      result => {
        addToHistory(query);
        query_results[query] = { result };
        window.history.replaceState(null, "", pageURL);
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
      submit(query);
    }
  }

  function queryUrl(query, format) {
    return urlFor("download_query", {
      query_string: query,
      result_format: format,
    });
  }

  onMount(() => {
    const url = new URL(window.location.toString());
    query_string = url.searchParams.get("query_string") || "";
    if (query_string) {
      submit(query_string);
    }

    const queryOptions = {
      value: query_string,
      mode: "beancount-query",
      extraKeys: {
        "Ctrl-Enter": () => submit(query_string),
        "Cmd-Enter": () => submit(query_string),
      },
      placeholder: _(
        "...enter a BQL query. 'help' to list available commands."
      ),
    };
    editor = CodeMirror(cm => {
      form.insertBefore(cm, form.firstChild);
    }, queryOptions);

    editor.on("change", cm => {
      query_string = cm.getValue();
    });

    editor.on("keyup", (cm, event) => {
      if (!cm.state.completionActive && !ignoreKey(event.key)) {
        CodeMirror.commands.autocomplete(cm, undefined, {
          completeSingle: false,
        });
      }
    });
  });
</script>

<form
  on:submit|preventDefault={() => submit(query_string)}
  bind:this={form}
  class="query-box"
  method="GET">
  <button type="submit" data-key="Ctrl/Cmd+Enter">{_('Submit')}</button>
</form>
<div>
  {#each query_result_array as [history_item, { result, error }] (history_item)}
    <details class="query-result" class:error>
      <summary on:click={() => click(history_item)}>
        <pre>
          <code>{history_item}</code>
        </pre>
        {#if result}
          <span class="spacer" />
          <span class="download">
            ({_('Download as')}
            <a href={queryUrl(history_item, 'csv')} data-remote>CSV</a>
            {#if $favaAPIStore.have_excel}
              ,
              <a href={queryUrl(history_item, 'xls')} data-remote>XLS</a>
              ,
              <a href={queryUrl(history_item, 'xlsx')} data-remote>XLSX</a>
              , or
              <a href={queryUrl(history_item, 'ods')} data-remote>ODS</a>
            {/if}
            )
          </span>
        {/if}
      </summary>
      <div>
        {#if result || error}
          {@html result || error}
        {/if}
      </div>
    </details>
  {/each}
</div>
