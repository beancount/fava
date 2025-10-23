<script lang="ts">
  import { urlFor } from "../../helpers.ts";
  import { _ } from "../../i18n.ts";
  import QueryTable from "../query/QueryTable.svelte";
  import EntriesByType from "./EntriesByType.svelte";
  import {
    postings_per_account_query,
    type StatisticsReportProps,
  } from "./index.ts";
  import UpdateActivity from "./UpdateActivity.svelte";

  let {
    all_balance_directives,
    balances,
    entries_by_type,
    postings_per_account,
  }: StatisticsReportProps = $props();
</script>

<div class="left">
  <h3>
    {_("Postings per Account")}
    (<a href={$urlFor("query", { query_string: postings_per_account_query })}>
      {_("Query")}
    </a>)
  </h3>
  <QueryTable table={postings_per_account} />
</div>

<div class="left">
  <h3>
    {_("Update Activity")}
    <copyable-text
      class="button right"
      title={_(
        "Click to copy balance directives for accounts (except green ones) to the clipboard.",
      )}
      data-clipboard-text={all_balance_directives}
    >
      {_("Copy balance directives")}
    </copyable-text>
  </h3>
  <UpdateActivity {balances} />
</div>

<div class="left">
  <h3>{_("Entries per Type")}</h3>
  <EntriesByType {entries_by_type} />
</div>
