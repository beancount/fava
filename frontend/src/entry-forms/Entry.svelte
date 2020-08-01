<script>
  import Balance from "./Balance.svelte";
  import Note from "./Note.svelte";
  import Transaction from "./Transaction.svelte";

  /** @type {import('../entries').Entry} */
  export let entry;

  const components = { Balance, Note, Transaction };

  $: component = components[entry.type];
</script>

<svelte:component this={component} bind:entry />
