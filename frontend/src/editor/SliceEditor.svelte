<script lang="ts">
  import { put } from "../api";
  import { initBeancountEditor } from "../codemirror/setup";
  import { _ } from "../i18n";
  import { notify_err } from "../notifications";
  import router from "../router";
  import { closeOverlay } from "../stores";
  import { reloadAfterSavingEntrySlice } from "../stores/editor";

  import SaveButton from "./SaveButton.svelte";

  export let slice: string;
  export let entry_hash: string;
  export let sha256sum: string;

  let currentSlice = slice;
  $: changed = currentSlice !== slice;

  let saving = false;

  async function save() {
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

  const [, useEditor] = initBeancountEditor(
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
    ]
  );
</script>

<form on:submit|preventDefault={save}>
  <div class="editor" use:useEditor />
  <div class="flex-row">
    <span class="spacer" />
    <label>
      <input type="checkbox" bind:checked={$reloadAfterSavingEntrySlice} />
      <span>{_("reload")}</span>
    </label>
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
