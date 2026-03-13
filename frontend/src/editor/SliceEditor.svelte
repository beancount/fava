<script lang="ts">
  import { SvelteURL } from "svelte/reactivity";

  import {
    delete_source_slice,
    get_context_balance,
    get_context_note,
    get_context_transaction,
    put_source_slice,
  } from "../api/index.ts";
  import { attach_editor } from "../codemirror/dom.ts";
  import type { CodemirrorBeancount } from "../codemirror/types.ts";
  import type { EntryBaseAttributes } from "../entries/index.ts";
  import { todayAsString } from "../format.ts";
  import { _ } from "../i18n.ts";
  import { notify_err } from "../notifications.ts";
  import { router } from "../router.ts";
  import { reloadAfterSavingEntrySlice } from "../stores/editor.ts";
  import { initial_entry } from "../stores/editor.ts";
  import { currency_column, indent } from "../stores/fava_options.ts";
  import DeleteButton from "./DeleteButton.svelte";
  import DuplicateButton from "./DuplicateButton.svelte";
  import SaveButton from "./SaveButton.svelte";

  interface Props {
    slice: string;
    entry_hash: string;
    entry: EntryBaseAttributes;
    sha256sum: string;
    codemirror_beancount: CodemirrorBeancount;
  }

  let {
    slice,
    entry_hash = $bindable(),
    entry,
    sha256sum = $bindable(),
    codemirror_beancount,
  }: Props = $props();

  // Keep the initital slice value to check for changes.
  // svelte-ignore state_referenced_locally
  const initial_slice = slice;

  let currentSlice = $state(initial_slice);
  let changed = $derived(currentSlice !== initial_slice);

  let saving = $state(false);
  let deleting = $state(false);

  async function save(event?: SubmitEvent) {
    event?.preventDefault();
    saving = true;
    try {
      sha256sum = await put_source_slice({
        entry_hash,
        source: currentSlice,
        sha256sum,
      });
      if ($reloadAfterSavingEntrySlice) {
        router.reload();
      }
      router.close_overlay();
    } catch (error) {
      notify_err(error, (err) => `Saving failed: ${err.message}`);
    } finally {
      saving = false;
    }
  }

  async function deleteSlice() {
    deleting = true;
    try {
      await delete_source_slice({ entry_hash, sha256sum });
      entry_hash = "";
      if ($reloadAfterSavingEntrySlice) {
        router.reload();
      }
      router.close_overlay();
    } catch (error) {
      notify_err(error, (err) => `Deleting failed: ${err.message}`);
    } finally {
      deleting = false;
    }
  }

  async function duplicate(): Promise<void> {
    try {
      switch (entry.t) {
        case "Balance":
          initial_entry.set(
            (await get_context_balance({ entry_hash })).entry.set(
              "date",
              todayAsString(),
            ),
          );
          break;
        case "Note":
          initial_entry.set(
            (await get_context_note({ entry_hash })).entry.set(
              "date",
              todayAsString(),
            ),
          );
          break;
        case "Transaction":
          initial_entry.set(
            (await get_context_transaction({ entry_hash })).entry.set(
              "date",
              todayAsString(),
            ),
          );
          break;
        default:
          throw new Error(
            `Duplication of entry type ${entry.t} not supported.`,
          );
      }

      // Open the "Add Entry" dialog pre-filled with this entry's data.
      // AddEntry will detect the type (Transaction/Note/Balance)
      // and switch tabs.
      const url = new SvelteURL(router.current);
      url.hash = "#add-transaction";
      router.navigate(url);
    } catch (error) {
      notify_err(error, (err) => `Duplication failed: ${err.message}`);
    }
  }

  // svelte-ignore state_referenced_locally
  const editor = codemirror_beancount.init_beancount_editor(
    initial_slice,
    (state) => {
      currentSlice = state.sliceDoc();
    },
    [
      {
        key: "Control-s",
        mac: "Meta-s",
        run: () => {
          save().catch(() => {
            // save should catch all errors itself, see above
          });
          return true;
        },
      },
    ],
    $indent,
    $currency_column,
  );
</script>

<form onsubmit={save} class="flex-column">
  <div class="editor" {@attach attach_editor(editor)}></div>
  <div class="flex-row">
    {#if entry.t === "Balance" || entry.t === "Note" || entry.t === "Transaction"}
      <DuplicateButton onDuplicate={duplicate} />
    {/if}
    <span class="spacer"></span>
    <label>
      <input type="checkbox" bind:checked={$reloadAfterSavingEntrySlice} />
      <span>{_("reload")}</span>
    </label>
    <DeleteButton {deleting} onDelete={deleteSlice} />
    <SaveButton {changed} {saving} />
  </div>
</form>

<style>
  .editor {
    border: 1px solid var(--sidebar-border);
  }
</style>
