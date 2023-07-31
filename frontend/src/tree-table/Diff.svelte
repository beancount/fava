<script lang="ts">
  import { ctx } from "../stores/format";

  /** Difference to show. */
  export let diff: number;
  /** Number to show on hover. */
  export let num: number;
  /** The currency that both numbers are in. */
  export let currency: string;
</script>

<br />
<span class:positive={diff > 0} title={$ctx.amount(num, currency)}>
  ({$ctx.num(diff, currency)})
</span>

<style>
  span {
    margin-right: 3px;
    font-size: 0.9em;
    color: var(--budget-negative);
    white-space: nowrap;
  }

  .positive {
    color: var(--budget-positive);
  }
</style>
