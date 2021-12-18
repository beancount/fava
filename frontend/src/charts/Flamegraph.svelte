<script lang="ts">
  import "d3-flame-graph/dist/d3-flamegraph.css";
  import type { FlameGraph } from "d3-flame-graph";

  import { flamegraph } from "d3-flame-graph";
  import { select } from "d3-selection";
  import { onDestroy, onMount } from "svelte";

  import { ctx, formatPercentage } from "../format";

  import type { AccountHierarchyNode } from "./hierarchy";

  export let data: AccountHierarchyNode;
  export let width: number;
  export let currency: string;
  let details: HTMLDivElement;
  let container: HTMLDivElement;

  let chart: FlameGraph | null = null;
  const lastAccount = /(^|:)([^:]*)$/;

  function labelText(d: AccountHierarchyNode) {
    const val = d.value || 0;
    const rootValue = data.value || 1;

    return `${$ctx.currency(val)} ${currency} (${formatPercentage(
      val / rootValue
    )}) ${d.data.data.account}`;
  }

  onMount(async () => {
    chart = flamegraph()
      .label(labelText)
      .cellHeight(18)
      // svelte-ignore
      .setDetailsElement(details);
    // Suppress 'getName' property not found error.
    // Remove the suppression once
    // https://github.com/spiermar/d3-flame-graph/pull/205
    // is merged and released.
    // @ts-ignore
    chart.getName((d: AccountHierarchyNode) => {
      const m = lastAccount.exec(d.data.data.account);
      if (m) {
        return m[2];
      }
      return "";
    });
  });

  onDestroy(() => {
    if (chart) {
      chart.destroy();
      chart = null;
    }
  });

  $: if (data && chart) {
    chart.width(width);
    // Reset the chart legend on chart change.
    select(container).datum(data).call(chart);
  }
</script>

<div bind:this={container} {width} />
<div bind:this={details} style="height: 1.2em;" />
