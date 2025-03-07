<script lang="ts">
  import type { LanguageSupport } from "@codemirror/language";

  import { doDelete, put } from "../api";
  import { initBeancountEditor } from "../codemirror/setup";
  import { _ } from "../i18n";
  import { notify_err } from "../notifications";
  import router from "../router";
  import { reloadAfterSavingEntrySlice } from "../stores/editor";
  import { closeOverlay } from "../stores/url";
  import DeleteButton from "./DeleteButton.svelte";
  import SaveButton from "./SaveButton.svelte";

  interface Props {
    beancount_language_support: LanguageSupport;
    slice: string;
    entry_hash: string;
    sha256sum: string;
  }

  let {
    beancount_language_support,
    slice,
    entry_hash = $bindable(),
    sha256sum = $bindable(),
  }: Props = $props();

  let currentSlice = $state(slice);
  let changed = $derived(currentSlice !== slice);

  let saving = $state(false);
  let deleting = $state(false);

  async function save(event?: SubmitEvent) {
    event?.preventDefault();
    saving = true;
    try {
      sha256sum = await put("source_slice", {
        entry_hash,
        source: currentSlice,
        sha256sum,
      });
      if ($reloadAfterSavingEntrySlice) {
        router.reload();
      }
      closeOverlay();
    } catch (error) {
      notify_err(error, (err) => `Saving failed: ${err.message}`);
    } finally {
      saving = false;
    }
  }

  async function deleteSlice() {
    deleting = true;
    try {
      await doDelete("source_slice", { entry_hash, sha256sum });
      entry_hash = "";
      if ($reloadAfterSavingEntrySlice) {
        router.reload();
      }
      closeOverlay();
    } catch (error) {
      notify_err(error, (err) => `Deleting failed: ${err.message}`);
    } finally {
      deleting = false;
    }
  }

  const { renderEditor } = initBeancountEditor(
    slice,
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
    beancount_language_support,
  );
</script>

<form onsubmit={save}>
  <div class="editor" use:renderEditor></div>
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
