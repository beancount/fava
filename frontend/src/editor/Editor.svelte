<script>
  import { CodeMirror } from "../editor";

  /** @type {string} */
  export let value;

  /** @type {CodeMirror.Editor | undefined} */
  let editor;

  $: if (editor && value !== editor.getValue()) {
    editor.setValue(value);
  }

  /**
   * @param {HTMLElement} div
   */
  function initialiseEditor(div) {
    editor = CodeMirror(div, {
      readOnly: true,
      lineNumbers: true,
      value,
    });
    editor.on("changes", (cm) => {
      value = cm.getValue();
    });
  }
</script>

<div use:initialiseEditor />

<style>
  div {
    width: 100%;
    height: 100%;
  }
  div :global(.CodeMirror-lines) {
    border-top: 1px solid var(--color-sidebar-border);
  }
  div :global(.CodeMirror) {
    width: 100%;
    height: 100%;
    margin: 0;
    border: 0;
  }
</style>
