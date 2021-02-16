<script lang="ts">
  import { initQueryEditor } from "../codemirror/setup";
  import { _ } from "../i18n";
  import { keyboardShortcut } from "../keyboard-shortcuts";

  export let value: string;
  export let submit: () => void;

  const [editor, useEditor] = initQueryEditor(
    value,
    (s) => {
      value = s.doc.toString();
    },
    _("...enter a BQL query. 'help' to list available commands."),
    submit
  );

  $: if (value !== editor.state.doc.toString()) {
    editor.dispatch({
      changes: { from: 0, to: editor.state.doc.length, insert: value },
    });
  }
</script>

<form on:submit|preventDefault={submit}>
  <div use:useEditor />
  <button type="submit" use:keyboardShortcut={"Control+Enter"}>
    {_("Submit")}
  </button>
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

  div {
    flex-grow: 1;
    width: 100%;
    height: auto;
    margin-right: 0.5em;
    font-size: 16px;
    border: 1px solid var(--color-background-darker);
  }

  form :global(.cm-wrap) {
    width: 100%;
  }
</style>
