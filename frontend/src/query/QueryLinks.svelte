<script>
  import { urlFor } from "../helpers";
  import { _ } from "../i18n";
  import { HAVE_EXCEL } from "../stores";

  /** @type {string} */
  export let query;

  /**
   * URL to download a query.
   * @param {string} query_string
   * @param {string} format
   */
  function queryUrl(query_string, format) {
    return urlFor(`download-query/query_result.${format}`, {
      query_string,
    });
  }
</script>

<span>
  ({_("Download as")}
  <a href={queryUrl(query, "csv")} data-remote>CSV</a>
  {#if $HAVE_EXCEL}
    ,
    <a href={queryUrl(query, "xls")} data-remote>XLS</a>
    ,
    <a href={queryUrl(query, "xlsx")} data-remote>XLSX</a>
    , or
    <a href={queryUrl(query, "ods")} data-remote>ODS</a>
  {/if}
  )
</span>

<style>
  span {
    color: var(--color-text-lighter);
  }
</style>
