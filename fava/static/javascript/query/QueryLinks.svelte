<script>
  import { _, urlFor } from "../helpers";
  import { favaAPIStore } from "../stores";

  export let query = "";

  function queryUrl(query_string, format) {
    return urlFor(`download-query/query_result.${format}`, {
      query_string: query,
    });
  }
</script>

<span class="download">
  ({_('Download as')}
  <a href={queryUrl(query, 'csv')} data-remote>CSV</a>
  {#if $favaAPIStore.have_excel}
    ,
    <a href={queryUrl(query, 'xls')} data-remote>XLS</a>
    ,
    <a href={queryUrl(query, 'xlsx')} data-remote>XLSX</a>
    , or
    <a href={queryUrl(query, 'ods')} data-remote>ODS</a>
  {/if}
  )
</span>
