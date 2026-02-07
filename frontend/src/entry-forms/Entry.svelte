<script lang="ts">
  import type { Entry } from "../entries/index.ts";
  import { Balance, Note, Transaction } from "../entries/index.ts";
  import BalanceSvelte from "./Balance.svelte";
  import NoteSvelte from "./Note.svelte";
  import TransactionSvelte from "./Transaction.svelte";

  interface Props {
    entry: Entry;
    duplicate?: boolean;
  }

  let { entry = $bindable(), duplicate = false }: Props = $props();
</script>

<div class="flex-column" class:duplicate>
  {#if entry instanceof Balance}
    <BalanceSvelte bind:entry />
  {:else if entry instanceof Note}
    <NoteSvelte bind:entry />
  {:else if entry instanceof Transaction}
    <TransactionSvelte bind:entry />
  {:else}
    Entry type unsupported for editing.
  {/if}
</div>

<style>
  .duplicate {
    opacity: 0.5;
  }
</style>
