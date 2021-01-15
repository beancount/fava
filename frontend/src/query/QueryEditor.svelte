<script>
  import { createEventDispatcher } from "svelte";

  import { initQueryEditor } from "./query-editor";
  import { keyboardShortcut } from "../keyboard-shortcuts";
  import { _ } from "../i18n";

  /** @type {string} */
  export let value;
  /** @type {import('@codemirror/view').EditorView} */
  let editor;

  const dispatch = createEventDispatcher();
  const submit = () => dispatch("submit");

  $: if (editor && value !== editor.state.doc.toString()) {
    editor.dispatch({
      changes: { from: 0, to: editor.state.doc.length, insert: value },
    });
  }

  /**
   * @param {HTMLElement} form
   */
  function queryEditor(form) {
    editor = initQueryEditor(
      value,
      (v) => {
        value = v;
      },
      submit
    );

    form.insertBefore(editor.dom, form.firstChild);
  }
</script>

<form use:queryEditor on:submit|preventDefault={submit}>
  <button type="submit" use:keyboardShortcut={"Control+Enter"}
    >{_("Submit")}</button
  >
</form>

<style>
  form {
    display: flex;
    align-items: center;
    padding-bottom: 1em;
  }

  button {
    margin: 0;
  }

  form :global(.cm-wrap) {
    flex-grow: 1;
    width: 100%;
    height: auto;
    margin: 0;
    margin-right: 0.5em;
    font-family: var(--font-family-editor);
    font-size: 16px;
    border: 1px solid var(--color-background-darker);
  }
</style>
