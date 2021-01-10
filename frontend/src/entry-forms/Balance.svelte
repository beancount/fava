<script>
  import { _ } from "../i18n";
  import { currencies } from "../stores";

  import AutocompleteInput from "../AutocompleteInput.svelte";
  import AccountInput from "./AccountInput.svelte";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadata from "./EntryMetadata.svelte";

  /** @type {import("../entries").Balance} */
  export let entry;
</script>

<div>
  <div class="flex-row">
    <input type="date" bind:value={entry.date} required />
    <h4>{_("Balance")}</h4>
    <AccountInput className="grow" bind:value={entry.account} />
    <input
      type="tel"
      pattern="-?[0-9.,]*"
      placeholder={_("Number")}
      size={10}
      bind:value={entry.amount.number}
    />
    <AutocompleteInput
      className="currency"
      placeholder={_("Currency")}
      suggestions={$currencies}
      bind:value={entry.amount.currency}
    />
    <AddMetadataButton bind:meta={entry.meta} />
  </div>
  <EntryMetadata bind:meta={entry.meta} />
</div>

<style>
  div :global(.currency) {
    width: 6em;
  }
</style>
