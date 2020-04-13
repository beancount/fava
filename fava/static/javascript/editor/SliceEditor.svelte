<script>
  import { putAPI } from "../helpers";
  import { notify } from "../notifications";
  import e from "../events";
  import router from "../router";
  import { closeOverlay } from "../stores";
  import {
    CodeMirror,
    sourceEditorOptions,
    enableAutomaticCompletions,
  } from "../editor";

  import SaveButton from "./SaveButton.svelte";

  export let slice;
  export let entry_hash;
  export let sha256sum;

  let editor;
  let changed = false;
  let saving = false;

  async function save() {
    saving = true;
    try {
      sha256sum = await putAPI("source_slice", {
        entry_hash,
        source: slice,
        sha256sum,
      });
      changed = false;
      editor.getDoc().markClean();
      e.trigger("file-modified");
      router.reload();
      closeOverlay();
    } catch (error) {
      notify(error, "error");
    } finally {
      saving = false;
    }
  }

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

<style>
  div :global(.CodeMirror) {
    height: auto;
  }
</style>

<form on:submit|preventDefault={save}>
  <div use:sourceSliceEditor />
  <SaveButton {changed} {saving} />
</form>
