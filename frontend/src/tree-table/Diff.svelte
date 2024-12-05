<script lang="ts">
  import { ctx } from "../stores/format";

  interface Props {
    /** Difference to show. */
    diff: number;
    /** Number to show on hover. */
    num: number;
    /** The currency that both numbers are in. */
    currency: string;
  }

  let { diff, num, currency }: Props = $props();
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
