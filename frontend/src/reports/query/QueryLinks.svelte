<!--
  @component
  Renders the links to download the query result in CSV and possibly
  other formats.
-->
<script lang="ts">
  import { urlFor } from "../../helpers";
  import { _ } from "../../i18n";
  import { HAVE_EXCEL } from "../../stores";

  interface Props {
    /** The query string. */
    query: string;
  }

  let { query }: Props = $props();
  let params = $derived({ query_string: query });
</script>

<span>
  ({_("Download as")}
  <a href={$urlFor("download-query/query_result.csv", params)} data-remote>
    CSV
  </a>
  {#if $HAVE_EXCEL}
    ,
    <a href={$urlFor("download-query/query_result.xlsx", params)} data-remote>
      XLSX
    </a>
    , or
    <a href={$urlFor("download-query/query_result.ods", params)} data-remote>
      ODS
    </a>
  {/if}
  )
</span>

<style>
  span {
    color: var(--text-color-lighter);
  }
</style>
