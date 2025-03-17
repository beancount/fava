<script lang="ts">
  import type { Entry } from "../entries";
  import { Balance, Note, Transaction } from "../entries";
  import BalanceSvelte from "./Balance.svelte";
  import NoteSvelte from "./Note.svelte";
  import TransactionSvelte from "./Transaction.svelte";

  interface Props {
    entry: Entry;
  }

  let { entry = $bindable() }: Props = $props();
</script>

{#if entry instanceof Balance}
  <BalanceSvelte bind:entry />
{:else if entry instanceof Note}
  <NoteSvelte bind:entry />
{:else if entry instanceof Transaction}
  <TransactionSvelte bind:entry />
{:else}
  Entry type unsupported for editing.
{/if}
