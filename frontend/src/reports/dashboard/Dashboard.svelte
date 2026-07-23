<script lang="ts">
  import ChartSwitcher from "../../charts/ChartSwitcher.svelte";
  import type { DashboardReportProps } from "./index.ts";

  let { charts }: DashboardReportProps = $props();
</script>

<ChartSwitcher {charts} />
