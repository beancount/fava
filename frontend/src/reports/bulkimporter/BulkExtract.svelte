<script lang="ts">
  import type { Entry as EntryType } from "../../entries";
  import { _ } from "../../i18n";
  import ModalBase from "../../modals/ModalBase.svelte";
  import SimpleTransactionRow from "./SimpleTransactionRow.svelte";
  import { accounts } from "../../stores";
  import { slide } from "svelte/transition";

  import { SimpleTransaction } from ".";
  import { Transaction } from "../../entries";
  import AutocompleteInput from "../../AutocompleteInput.svelte";
  import OtherEntryRow from "./OtherEntryRow.svelte";
  import IndividualEntryEdit from "./IndividualEntryEdit.svelte";

  export let entries: EntryType[];
  export let save: () => void;
  export let close: () => void;
  export let account: string;

  // The new target account (when moving simple transactions in bulk).
  let new_target: string;
  // The entry that we want to manually edit. Starts off undefined, is set when
  // the user clicks the vertical elipses to edit, and unset when they close the
  // editor.
  let entry_to_edit: EntryType | undefined = undefined;

  // Simple transactions grouped by their target account.
  let transactions_by_target: Map<string, SimpleTransaction[]>;
  let simple_transactions: SimpleTransaction[];
  let other_entries: EntryType[];
  $: {
    // When `entries` changes, we recompute simple_transactions, other_entries,
    // and transactions_by_target.
    simple_transactions = [];
    other_entries = [];
    entries.forEach((entry) => {
      try {
        if (entry instanceof Transaction) {
          simple_transactions.push(
            new SimpleTransaction(entry, account, simple_transactions.length),
          );
          return;
        }
      } finally {
      }
      other_entries.push(entry);
    });
    transactions_by_target = new Map();
    simple_transactions.forEach((st) => {
      let target = st.getTargetAccount();
      let transactions = transactions_by_target.get(target);
      if (transactions) {
        transactions.push(st);
      } else {
        transactions_by_target.set(target, [st]);
      }
    });
  }
  // `selected` shouldn't always be regenerated after changes to `entries`
  // because Svelte sometimes recomputes when there isn't a real change to
  // `entries` and the user might still be selecting transactions. Only recreate
  // `selected` if there is a length mismatch.
  let selected: boolean[] = [];
  $: if (selected.length !== simple_transactions.length) {
    selected = new Array(simple_transactions.length).fill(false);
  }
  $: shown = entries.length > 0;
  $: num_selected = selected.filter((v) => v).length;

  function selectNone() {
    selected.fill(false);
    selected = selected;
  }

  function selectAll() {
    selected.fill(true);
    selected = selected;
  }

  function toggleSelectAll() {
    if (num_selected == 0) {
      selectAll();
    } else {
      selectNone();
    }
  }

  function forEachSelectedTransaction(
    callbackFn: (transaction: SimpleTransaction, index: number) => void,
  ) {
    selected.forEach((selected, index) => {
      if (selected) {
        callbackFn(simple_transactions[index]!, index);
      }
    });
  }

  function moveSelected() {
    if (!new_target) {
      return;
    }
    forEachSelectedTransaction((transaction, index) => {
      transaction.transaction.postings[
        transaction.target_posting_index
      ]!.account = new_target;
    });
    // Force reactivity to everything that follows from `entries`
    entries = entries;
    new_target = "";
    selectNone();
  }

  function markSelectedDuplicate() {
    forEachSelectedTransaction((transaction, index) => {
      transaction.transaction.meta.__duplicate__ = true;
    });
    // Force reactivity to everything that follows from `entries`
    entries = entries;
    selectNone();
  }

  function markSelectedNotDuplicate() {
    forEachSelectedTransaction((transaction, index) => {
      transaction.transaction.meta.__duplicate__ = false;
    });
    // Force reactivity to everything that follows from `entries`
    entries = entries;
    selectNone();
  }
</script>

<ModalBase {shown} closeHandler={close}>
  <div>
    <h3>{_("Import")}: {account}</h3>
    <div class="toolbar" transition:slide|global>
      <label>
        <input type="checkbox" on:click|preventDefault={toggleSelectAll} />
        {num_selected} selected.
      </label>
      {#if num_selected > 0}
        <AutocompleteInput
          bind:value={new_target}
          placeholder={_("Move to account")}
          suggestions={$accounts}
          className="account-selector"
        />
        <button on:click={moveSelected}>Move</button>
        <button on:click={markSelectedDuplicate}>Mark Duplicate</button>
        <button on:click={markSelectedNotDuplicate}>Mark Not Duplicate</button>
      {/if}
    </div>
    <div>
      {#each transactions_by_target as [target, transactions], i}
        <h4>{target}</h4>
        <ul class="flex-table bulk-importer">
          <li class="head">
            <p>
              <span class="select"></span>
              <span class="datecell">Date</span>
              <span class="flag">F</span>
              <span class="description">Description</span>
              <span class="num">Amount</span>
              <span class="edit"></span>
            </p>
          </li>
          {#each transactions as transaction}
            <SimpleTransactionRow
              bind:entry={transaction}
              bind:selected={selected[transaction.index]}
              manual_edit={() => {
                entry_to_edit = transaction.transaction;
              }}
            />
          {/each}
        </ul>
      {/each}
      <strong>{_("Other entries")}</strong>
      <ul class="flex-table bulk-importer">
        <li class="head">
          <p>
            <span class="select"></span>
            <span class="datecell">Date</span>
            <span class="flag">F</span>
            <span class="description">Description</span>
            <span class="num">Amount</span>
            <span class="edit"></span>
          </p>
        </li>
        {#each other_entries as entry}
          <OtherEntryRow
            bind:entry
            manual_edit={() => {
              entry_to_edit = entry;
            }}
          />
        {/each}
      </ul>
    </div>
    <div class="flex-row">
      <form on:submit|preventDefault={save}>
        <button>{_("Save")}</button>
      </form>
    </div>
  </div>
  <IndividualEntryEdit
    bind:entry={entry_to_edit}
    close={() => {
      entry_to_edit = undefined;
      entries = entries;
    }}
  />
</ModalBase>

<style>
  .toolbar {
    min-height: 3em;
  }

  .toolbar label {
    vertical-align: middle;
  }
</style>
