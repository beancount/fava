<script lang="ts">
  import { get_context, save_entries } from "../api/index.ts";
  import { Balance, Note, Transaction } from "../entries/index.ts";
  import Entry from "../entry-forms/Entry.svelte";
  import { todayAsString } from "../format.ts";
  import { _ } from "../i18n.ts";
  import type { Result } from "../lib/result.ts";
  import { Err } from "../lib/result.ts";
  import type { ValidationError } from "../lib/validation.ts";
  import { router } from "../router.ts";
  import { addEntryContinue } from "../stores/editor.ts";
  import { hash } from "../stores/url.ts";
  import ModalBase from "./ModalBase.svelte";

  /** The entry types which have support adding in the modal. */
  const entryTypes = [
    [Transaction, _("Transaction")],
    [Balance, _("Balance")],
    [Note, _("Note")],
  ] as const;

  // For the first entry to be added, use today as the default date.
  let entry: Transaction | Balance | Note = $state.raw(
    Transaction.empty(todayAsString()),
  );
  let error: ValidationError | null = $state(null);

  async function submit(event: SubmitEvent) {
    event.preventDefault();
    await save_entries([entry]);
    const added_entry_date = entry.date;
    // Reuse the date of the entry that was just added.
    // @ts-expect-error all these entries have that static method, but TS is not able to determine that
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
    entry = entry.constructor.empty(added_entry_date);
    if (!$addEntryContinue) {
      router.close_overlay();
    }
  }

  let shown = $derived($hash.startsWith("add-transaction"));
  let entry_hash = $derived(
    $hash.startsWith("add-transaction-from") ? $hash.slice(21) : "",
  );
  $effect(() => {
    async function fetchAndSet() {
      if (entry_hash) {
        const data = await get_context({ entry_hash });
        let fetchedEntry = data.entry;
        let result: Result<Transaction | Balance | Note, ValidationError>;
        if (fetchedEntry.t === "Transaction") {
          result = Transaction.validator(fetchedEntry);
        } else if (fetchedEntry.t === "Balance") {
          result = Balance.validator(fetchedEntry);
        } else if (fetchedEntry.t === "Note") {
          result = Note.validator(fetchedEntry);
        } else {
          result = new Err({
            name: "ValidationError",
            message: `This entry type is not supported.`,
          });
        }

        if (result.is_ok) {
          entry = result.value;
        } else {
          error = result.error;
        }
      }
    }
    fetchAndSet().catch(() => {
      error = { name: "ValidationError", message: "Call to server failed." };
    });
  });
</script>

<ModalBase {shown} focus=".payee input">
  {#if error}
    <p>{_("Error loading entry. Error message:")} {error.message}</p>
  {:else}
    <form onsubmit={submit} class="flex-column">
      <h3>
        {_("Add")}
        {#each entryTypes as [Cls, displayName] (displayName)}
          <button
            type="button"
            class:muted={!(entry instanceof Cls)}
            onclick={() => {
              // when switching between entry types, keep the date.
              entry = Cls.empty(entry.date);
            }}
          >
            {displayName}
          </button>
          <!-- eslint-disable-next-line svelte/no-useless-mustaches -->
          {" "}
        {/each}
      </h3>
      <Entry bind:entry />
      <div class="flex-row">
        <span class="spacer"></span>
        <label>
          <input type="checkbox" bind:checked={$addEntryContinue} />
          <span>{_("continue")}</span>
        </label>
        <button type="submit">{_("Save")}</button>
      </div>
    </form>
  {/if}
</ModalBase>

<style>
  h3 {
    margin: 0;
  }

  label span {
    margin-right: 1rem;
  }
</style>
