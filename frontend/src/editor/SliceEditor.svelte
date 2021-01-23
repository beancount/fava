<script>
  import { put } from "../api";
  import { notify } from "../notifications";
  import router from "../router";
  import { closeOverlay } from "../stores";

  import SaveButton from "./SaveButton.svelte";
  import { initBeancountEditor } from "../codemirror/setup";

  /** @type {string} */
  export let slice;
  /** @type {string} */
  export let entry_hash;
  /** @type {string} */
  export let sha256sum;

  let changed = false;
  const onDocChanges = () => {
    changed = true;
  };

  const [editor, useEditor] = initBeancountEditor(slice, onDocChanges, []);

  let saving = false;

  async function save() {
    saving = true;
    try {
      slice = editor.state.doc.toString();
      sha256sum = await put("source_slice", {
        entry_hash,
        source: slice,
        sha256sum,
      });
      changed = false;
      router.reload();
      closeOverlay();
    } catch (error) {
      notify(error, "error");
    } finally {
      saving = false;
    }
  }
</script>

<form on:submit|preventDefault={save}>
  <div use:useEditor />
  <SaveButton {changed} {saving} />
</form>

<style>
  form :global(.cm-wrap) {
    margin-bottom: 0.5rem;
    border: 1px solid var(--color-sidebar-border);
  }
</style>
