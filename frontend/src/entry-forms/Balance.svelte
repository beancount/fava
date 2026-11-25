<script lang="ts">
  import AutocompleteInput from "../components/AutocompleteInput.svelte";
  import type { Balance, EntryMetadata } from "../entries/index.ts";
  import { _ } from "../i18n.ts";
  import { evaluate_number_expression } from "../lib/number.ts";
  import { currencies } from "../stores/index.ts";
  import AccountInput from "./AccountInput.svelte";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadataSvelte from "./EntryMetadata.svelte";

  interface Props {
    entry: Balance;
  }

  let { entry = $bindable() }: Props = $props();

  // Keep local expression text separate from entry.amount.number while still
  // syncing when the parent updates or replaces the entry externally.
  const initial_entry = entry;

  let number_input: HTMLInputElement | undefined = $state.raw();
  let synced_entry = initial_entry;
  let raw_number = $state.raw(initial_entry.amount.number);

  function update_entry(next: Balance): void {
    entry = next;
    synced_entry = entry;
  }

  $effect(() => {
    if (entry !== synced_entry) {
      synced_entry = entry;
      raw_number = entry.amount.number;
    }
    const msg =
      raw_number === "" || evaluate_number_expression(raw_number).is_ok
        ? ""
        : _("Invalid number or arithmetic expression.");
    number_input?.setCustomValidity(msg);
  });
</script>

<div class="flex-row">
  <input
    type="date"
    bind:value={
      () => entry.date,
      (date: string) => {
        update_entry(entry.set("date", date));
      }
    }
    required
  />
  <h4>{_("Balance")}</h4>
  <AccountInput
    bind:value={
      () => entry.account,
      (account: string) => {
        update_entry(entry.set("account", account));
      }
    }
    date={entry.date}
    required
    --autocomplete-wrapper-flex="1"
  />
  <input
    type="text"
    placeholder={_("Number")}
    size={10}
    bind:this={number_input}
    bind:value={
      () => raw_number,
      (value: string) => {
        raw_number = value;
        if (value === "") {
          update_entry(entry.set("amount", entry.amount.set_number("")));
          return;
        }
        const res = evaluate_number_expression(value);
        if (res.is_ok) {
          update_entry(entry.set("amount", entry.amount.set_number(res.value)));
        }
      }
    }
    required
  />
  <AutocompleteInput
    placeholder={_("Currency")}
    suggestions={$currencies}
    bind:value={
      () => entry.amount.currency,
      (currency: string) => {
        update_entry(entry.set("amount", entry.amount.set_currency(currency)));
      }
    }
    required
    --autocomplete-wrapper-flex="0 6em"
  />
  <AddMetadataButton
    bind:meta={
      () => entry.meta,
      (meta: EntryMetadata) => {
        update_entry(entry.set("meta", meta));
      }
    }
  />
</div>
<EntryMetadataSvelte
  bind:meta={
    () => entry.meta,
    (meta: EntryMetadata) => {
      update_entry(entry.set("meta", meta));
    }
  }
/>
