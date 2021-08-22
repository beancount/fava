<script lang="ts">
  import type { Entry } from "../entries";

  import Balance from "./Balance.svelte";
  import Note from "./Note.svelte";
  import Transaction from "./Transaction.svelte";

  export let entry: Entry;

  const components = { Balance, Note, Transaction };

  $: component = components[entry.type];
</script>

<svelte:component this={component} bind:entry />
