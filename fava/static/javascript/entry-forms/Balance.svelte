<script>
  import { Posting } from "../entries";
  import { _ } from "../helpers";

  import AccountInput from "./AccountInput.svelte";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadata from "./EntryMetadata.svelte";

  // TODO change amount

  export let entry;
</script>
<div class="entry-form balance">
  <div class="fieldset">
    <input type="date" bind:value="{entry.date}" required />
    <h4>{_('Balance')}</h4>
    <AccountInput bind:value="{entry.account}" />
    <input
      type="tel"
      class="number"
      pattern="[0-9.,]*"
      placeholder="{_('Number')}"
      value="{entry.amount ? entry.amount.number : '' }"
    />
    <input
      type="text"
      class="currency"
      placeholder="{_('Currency')}"
      list="currencies"
      value="{entry.amount ? entry.amount.currency : '' }"
    />
    <AddMetadataButton bind:meta="{entry.meta}" />
  </div>
  <EntryMetadata bind:meta="{entry.meta}" />
</div>
