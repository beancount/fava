<script>
  import { _, urlFor } from "../helpers";
  import { HAVE_EXCEL } from "../stores";

  export let query = "";

  function queryUrl(query_string, format) {
    return urlFor(`download-query/query_result.${format}`, {
      query_string: query,
    });
  }
</script>

<style>
  span {
    color: var(--color-text-lighter);
  }
</style>

<span>
  ({_('Download as')}
  <a href={queryUrl(query, 'csv')} data-remote>CSV</a>
  {#if $HAVE_EXCEL}
    ,
    <a href={queryUrl(query, 'xls')} data-remote>XLS</a>
    ,
    <a href={queryUrl(query, 'xlsx')} data-remote>XLSX</a>
    , or
    <a href={queryUrl(query, 'ods')} data-remote>ODS</a>
  {/if}
  )
</span>
