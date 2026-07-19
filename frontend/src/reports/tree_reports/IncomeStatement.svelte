<script lang="ts">
  import ChartSwitcher from "../../charts/ChartSwitcher.svelte";
  import SelectCombobox from "../../charts/SelectCombobox.svelte";
  import { _, format } from "../../i18n.ts";
  import { getInterval, intervalLabel } from "../../lib/interval.ts";
  import { router } from "../../router.ts";
  import { average } from "../../stores/url.ts";
  import TreeTable from "../../tree-table/TreeTable.svelte";
  import type { TreeReportProps } from "./index.ts";

  const AVERAGES = ["", "day", "week", "month", "quarter", "year"] as const;

  let { charts, trees, date_range }: TreeReportProps = $props();
  let end = $derived(date_range?.end ?? null);

  const average_description = (option: string) => {
    if (option === "") {
      return _("No Average");
    }
    return format(_("%(interval)s average"), {
      interval: intervalLabel(getInterval(option)),
    });
  };
</script>

<SelectCombobox
  bind:value={
    () => $average,
    (value: string) => {
      router.set_search_param("average", value);
    }
  }
  options={AVERAGES}
  description={average_description}
/>

<ChartSwitcher {charts} />

<div class="row">
  <div class="column">
    {#each trees.slice(0, 2) as tree (tree.account)}
      <TreeTable {tree} {end} />
    {/each}
  </div>
  <div class="column">
    {#each trees.slice(2) as tree (tree.account)}
      <TreeTable {tree} {end} />
    {/each}
  </div>
</div>
