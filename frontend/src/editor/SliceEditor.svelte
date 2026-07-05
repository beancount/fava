<!--
  @component
  Edit the source slice of an entry or duplicate it.
-->
<script lang="ts">
  import {
    delete_source_slice,
    put_source_slice,
    save_entries,
  } from "../api/index.ts";
  import { attach_editor } from "../codemirror/dom.ts";
  import type { CodemirrorBeancount } from "../codemirror/types.ts";
  import {
    type EditableEntry,
    type Entry,
    is_editable,
  } from "../entries/index.ts";
  import EntrySvelte from "../entry-forms/Entry.svelte";
  import { todayAsString } from "../format.ts";
  import { _ } from "../i18n.ts";
  import { notify_err } from "../notifications.ts";
  import { router } from "../router.ts";
  import { reloadAfterSavingEntrySlice } from "../stores/editor.ts";
  import { currency_column, indent } from "../stores/fava_options.ts";
  import DeleteButton from "./DeleteButton.svelte";
  import SaveButton from "./SaveButton.svelte";

  interface Props {
    entry: Entry;
    slice: string;
    entry_hash: string;
    sha256sum: string;
    codemirror_beancount: CodemirrorBeancount;
  }

  let {
    entry,
    slice,
    entry_hash = $bindable(),
    sha256sum = $bindable(),
    codemirror_beancount,
  }: Props = $props();

  // Keep the initital slice value to check for changes.
  // svelte-ignore state_referenced_locally
  const initial_slice = slice;

  let current_slice = $state(initial_slice);
  let changed = $derived(current_slice !== initial_slice);

  let duplicated_entry = $state.raw<EditableEntry>();

  let saving = $state(false);

  async function save(event?: SubmitEvent) {
    event?.preventDefault();
    saving = true;
    try {
      sha256sum = await put_source_slice({
        entry_hash,
        source: current_slice,
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

  async function save_duplicated_entry(event: SubmitEvent) {
    event.preventDefault();
    try {
      if (duplicated_entry != null) {
        await save_entries([duplicated_entry]);
      }
      router.close_overlay();
    } finally {
      duplicated_entry = undefined;
    }
  }

  async function delete_slice() {
    try {
      await delete_source_slice({ entry_hash, sha256sum });
      entry_hash = "";
      if ($reloadAfterSavingEntrySlice) {
        router.reload();
      }
      router.close_overlay();
    } catch (error) {
      notify_err(error, (err) => `Deleting failed: ${err.message}`);
    }
  }

  // svelte-ignore state_referenced_locally
  const editor = codemirror_beancount.init_beancount_editor(
    initial_slice,
    (state) => {
      current_slice = state.sliceDoc();
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
    {#if is_editable(entry)}
      <button
        type="button"
        class="muted"
        onclick={() => {
          if (duplicated_entry == null) {
            duplicated_entry = entry.set("date", todayAsString());
          } else {
            duplicated_entry = undefined;
          }
        }}
      >
        {_("Duplicate")}
      </button>
    {/if}
    <span class="spacer"></span>
    <label>
      <input type="checkbox" bind:checked={$reloadAfterSavingEntrySlice} />
      <span>{_("reload")}</span>
    </label>
    <DeleteButton ondelete={delete_slice} />
    <SaveButton {changed} {saving} />
  </div>
</form>
{#if duplicated_entry}
  <form onsubmit={save_duplicated_entry} class="flex-column">
    <h3>{_("Add")} {_(duplicated_entry.t)}</h3>
    <EntrySvelte bind:entry={duplicated_entry} />
    <div class="flex-row">
      <span class="spacer"></span>
      <button type="submit">{_("Save")}</button>
    </div>
  </form>
{/if}

<style>
  .editor {
    border: 1px solid var(--sidebar-border);
  }

  h3 {
    margin-top: 0.5em;
  }
</style>
