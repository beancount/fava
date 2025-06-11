<script lang="ts">
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import type { Balance, EntryMetadata } from "../entries";
  import { _ } from "../i18n";
  import { currencies } from "../stores";
  import AccountInput from "./AccountInput.svelte";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadataSvelte from "./EntryMetadata.svelte";

  interface Props {
    entry: Balance;
  }

  let { entry = $bindable() }: Props = $props();
</script>

<div>
  <div class="flex-row">
    <input
      type="date"
      bind:value={
        () => entry.date,
        (date: string) => {
          entry = entry.set("date", date);
        }
      }
      required
    />
    <h4>{_("Balance")}</h4>
    <AccountInput
      className="grow"
      bind:value={
        () => entry.account,
        (account: string) => {
          entry = entry.set("account", account);
        }
      }
      date={entry.date}
      required
    />
    <input
      type="tel"
      pattern="-?[0-9.,]*"
      placeholder={_("Number")}
      size={10}
      bind:value={
        () => entry.amount.number,
        (number: string) => {
          entry = entry.set("amount", entry.amount.set_number(number));
        }
      }
      required
    />
    <AutocompleteInput
      className="currency"
      placeholder={_("Currency")}
      suggestions={$currencies}
      bind:value={
        () => entry.amount.currency,
        (currency: string) => {
          entry = entry.set("amount", entry.amount.set_currency(currency));
        }
      }
      required
    />
    <AddMetadataButton
      bind:meta={
        () => entry.meta,
        (meta: EntryMetadata) => {
          entry = entry.set("meta", meta);
        }
      }
    />
  </div>
  <EntryMetadataSvelte
    bind:meta={
      () => entry.meta,
      (meta: EntryMetadata) => {
        entry = entry.set("meta", meta);
      }
    }
  />
</div>

<style>
  div :global(.currency) {
    width: 6em;
  }
</style>
