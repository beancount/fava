<script lang="ts">
  import { delete_source_slice, put_source_slice } from "../api/index.ts";
  import { attach_editor } from "../codemirror/dom.ts";
  import type { CodemirrorBeancount } from "../codemirror/types.ts";
  import { _ } from "../i18n.ts";
  import { notify_err } from "../notifications.ts";
  import { router } from "../router.ts";
  import { reloadAfterSavingEntrySlice } from "../stores/editor.ts";
  import { currency_column, indent } from "../stores/fava_options.ts";
  import DeleteButton from "./DeleteButton.svelte";
  import SaveButton from "./SaveButton.svelte";

  interface Props {
    slice: string;
    entry_hash: string;
    sha256sum: string;
    codemirror_beancount: CodemirrorBeancount;
  }

  let {
    slice,
    entry_hash = $bindable(),
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

<form onsubmit={save}>
  <div class="editor" {@attach attach_editor(editor)}></div>
  <div class="flex-row">
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
  label span {
    margin-right: 1rem;
  }

  .editor {
    margin-bottom: 0.5rem;
    border: 1px solid var(--sidebar-border);
  }
</style>
