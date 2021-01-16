<script>
  import { initReadonlyEditor } from "./init-editor";
  /** @type {string} */
  export let value;

  /** @type {import('@codemirror/view').EditorView | undefined} */
  let editor;

  $: if (editor && value !== editor.state.doc.toString()) {
    editor.dispatch({
      changes: { from: 0, to: editor.state.doc.length, insert: value },
    });
  }

  /**
   * @param {HTMLElement} div
   */
  function initialiseEditor(div) {
    editor = initReadonlyEditor(value);
    div.appendChild(editor.dom);
  }
</script>

<div use:initialiseEditor />

<style>
  div {
    width: 100%;
    height: 100%;
  }
  div :global(.cm-wrap) {
    width: 100%;
    height: 100%;
    margin: 0;
    border: 0;
  }
</style>
