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
  let positive = $derived(diff > 0);
</script>

<br />
<span class:positive title={$ctx.amount(num, currency)}>
  ({positive ? "+" : "-"}{$ctx.num(Math.abs(diff), currency)})
</span>

<style>
  span {
    margin-right: 3px;
    font-size: 0.9em;
    color: var(--diff-negative);
    white-space: nowrap;
  }

  .positive {
    color: var(--diff-positive);
  }
</style>
