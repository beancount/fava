<script>
  import { _ } from "../helpers";
  import { favaAPI } from "../stores";

  import AutocompleteInput from "../AutocompleteInput.svelte";
  import AccountInput from "./AccountInput.svelte";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadata from "./EntryMetadata.svelte";

  export let entry;

  $: if (entry && !entry.amount) {
    entry.amount = {
      number: "",
      currency: "",
    };
  }
</script>

<div class="entry-form balance">
  <div class="fieldset">
    <input type="date" bind:value={entry.date} required />
    <h4>{_('Balance')}</h4>
    <AccountInput bind:value={entry.account} />
    <input
      type="tel"
      class="number"
      pattern="-?[0-9.,]*"
      placeholder={_('Number')}
      size="10"
      bind:value={entry.amount.number} />
    <AutocompleteInput
      className="currency"
      placeholder={_('Currency')}
      suggestions={favaAPI.currencies}
      bind:value={entry.amount.currency} />
    <AddMetadataButton bind:meta={entry.meta} />
  </div>
  <EntryMetadata bind:meta={entry.meta} />
</div>
