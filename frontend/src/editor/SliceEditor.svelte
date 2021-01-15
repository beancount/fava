<script>
  import { put } from "../api";
  import { notify } from "../notifications";
  import router from "../router";
  import { closeOverlay } from "../stores";
  import {
    CodeMirror,
    sourceEditorOptions,
    enableAutomaticCompletions,
  } from "../editor";

  import SaveButton from "./SaveButton.svelte";

  /** @type {string} */
  export let slice;
  /** @type {string} */
  export let entry_hash;
  /** @type {string} */
  export let sha256sum;

  /** @type {CodeMirror.Editor} */
  let editor;
  let changed = false;
  let saving = false;

  async function save() {
    saving = true;
    try {
      sha256sum = await put("source_slice", {
        entry_hash,
        source: slice,
        sha256sum,
      });
      changed = false;
      editor.getDoc().markClean();
      router.reload();
      closeOverlay();
    } catch (error) {
      notify(error, "error");
    } finally {
      saving = false;
    }
  }

  /**
   * @param {HTMLDivElement} div
   */
  function sourceSliceEditor(div) {
    const options = {
      ...sourceEditorOptions(save),
      value: slice,
    };
    editor = CodeMirror(div, options);
    enableAutomaticCompletions(editor);
    editor.on("changes", (cm) => {
      slice = cm.getValue();
      changed = !cm.getDoc().isClean();
    });
  }
</script>

<form on:submit|preventDefault={save}>
  <div use:sourceSliceEditor />
  <SaveButton {changed} {saving} />
</form>

<style>
  div :global(.CodeMirror) {
    height: auto;
  }
</style>
